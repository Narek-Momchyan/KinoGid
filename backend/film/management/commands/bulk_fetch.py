import os
import asyncio

from django.core.management.base import BaseCommand
from asgiref.sync import sync_to_async
from film.models import RawMovie
from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeVideo

load_dotenv()

TARGET_CHANNELS = ['@hayerenfilm', '@haykakanfilmerr']
DESTINATION_CHANNEL = '@kino_gid_2026'
MIN_DURATION = 1800  # 30 minutes in seconds

class Command(BaseCommand):
    help = 'Blindly bulk fetches movies from Telegram channels, forwards to our channel, and saves to RawMovie DB.'

    def handle(self, *args, **options):
        try:
            asyncio.run(self.process_channels())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nProcess interrupted by user."))

    async def get_video_duration(self, message):
        if not message.media:
            return 0
            
        if hasattr(message.media, 'document'):
            doc = message.media.document
            for attr in doc.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    return attr.duration
        return 0

    @sync_to_async
    def save_raw_movie(self, caption, telegram_message_id, source_channel):
        RawMovie.objects.create(
            original_caption=caption,
            telegram_message_id=telegram_message_id,
            source_channel=source_channel,
            is_processed=False
        )

    async def process_channels(self):
        api_id = os.environ.get('TELEGRAM_API_ID')
        api_hash = os.environ.get('TELEGRAM_API_HASH')
        session_string = os.environ.get('TELEGRAM_SESSION_STRING')
        
        if not all([api_id, api_hash, session_string]):
            self.stdout.write(self.style.ERROR("Missing required environment variables (TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_STRING)."))
            return

        client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
        self.stdout.write("Connecting to Telegram...")
        await client.start()

        try:
            for channel in TARGET_CHANNELS:
                self.stdout.write(self.style.SUCCESS(f"\n--- Processing channel: {channel} ---"))
                
                async for message in client.iter_messages(channel):
                    if not message.media or not (hasattr(message.media, 'document') or hasattr(message.media, 'video')):
                        continue
                        
                    duration = await self.get_video_duration(message)
                    if duration < MIN_DURATION:
                        continue # Skip short clips/trailers
                        
                    raw_caption = message.message or ''
                    if not raw_caption and hasattr(message.media, 'document'):
                        for attr in message.media.document.attributes:
                            if hasattr(attr, 'file_name') and attr.file_name:
                                raw_caption = attr.file_name
                                break
                    
                    def safe_print(text):
                        try:
                            self.stdout.write(text)
                        except UnicodeEncodeError:
                            self.stdout.write(text.encode('ascii', 'ignore').decode('ascii'))
                    
                    safe_print(f"Found long video (Duration: {duration}s) from {channel}")
                    
                    # Forward to our channel
                    safe_print(f"Forwarding to {DESTINATION_CHANNEL}...")
                    try:
                        sent_message = await client.forward_messages(
                            entity=DESTINATION_CHANNEL,
                            messages=message
                        )
                        new_telegram_message_id = sent_message.id
                    except Exception as e:
                        safe_print(self.style.ERROR(f"Failed to forward message: {e}"))
                        continue

                    # Save to DB
                    safe_print(f"Saving to database with message ID {new_telegram_message_id}...")
                    try:
                        await self.save_raw_movie(raw_caption, new_telegram_message_id, channel)
                    except Exception as db_err:
                        safe_print(self.style.ERROR(f"Database error: {db_err}"))
                    
                    safe_print(self.style.SUCCESS(f"Successfully processed! Sleeping for 45 seconds..."))
                    await asyncio.sleep(45)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical Error: {str(e)}"))
        finally:
            await client.disconnect()
