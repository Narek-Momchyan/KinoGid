import os
import asyncio
import urllib.parse
import aiohttp
import requests

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from asgiref.sync import sync_to_async
from film.models import Movie
from dotenv import load_dotenv

from telethon import TelegramClient, functions, types
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterDocument

load_dotenv()

class Command(BaseCommand):
    help = 'Fetches a movie via global Telegram search, forwards to channel, and saves to DB.'

    def add_arguments(self, parser):
        # Positional argument for the movie title
        parser.add_argument('title', type=str, help='Movie title to search on Telegram and TMDB')

    def handle(self, *args, **options):
        title = options['title']
        try:
            asyncio.run(self.process_movie(title))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nProcess interrupted by user."))

    async def process_movie(self, title):
        api_id = os.environ.get('TELEGRAM_API_ID')
        api_hash = os.environ.get('TELEGRAM_API_HASH')
        session_string = os.environ.get('TELEGRAM_SESSION_STRING')
        channel = os.environ.get('TELEGRAM_CHANNEL')
        tmdb_key = os.environ.get('TMDB_API_KEY')
        
        if not all([api_id, api_hash, session_string, channel, tmdb_key]):
            self.stdout.write(self.style.ERROR("Missing required environment variables (TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_STRING, TELEGRAM_CHANNEL, TMDB_API_KEY)."))
            return

        client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
        self.stdout.write(f"Connecting to Telegram...")
        await client.start()

        try:
            self.stdout.write(self.style.SUCCESS(f"\n--- Searching for: {title} ---"))

            # 1. Search globally on Telegram for video files
            self.stdout.write("Searching Telegram globally for video files...")
            result = await client(functions.messages.SearchGlobalRequest(
                q=title,
                filter=InputMessagesFilterVideo(),
                min_date=None,
                max_date=None,
                offset_rate=0,
                offset_peer=types.InputPeerEmpty(),
                offset_id=0,
                limit=5
            ))
            
            valid_message = None
            if result.messages:
                valid_message = result.messages[0]  # Take the first video result
            
            # Fallback: Sometimes videos are uploaded as documents instead of native videos
            if not valid_message:
                self.stdout.write("No native video found, trying document search...")
                result_doc = await client(functions.messages.SearchGlobalRequest(
                    q=title,
                    filter=InputMessagesFilterDocument(),
                    min_date=None,
                    max_date=None,
                    offset_rate=0,
                    offset_peer=types.InputPeerEmpty(),
                    offset_id=0,
                    limit=5
                ))
                if result_doc.messages:
                    for msg in result_doc.messages:
                        # Check if it has a video extension
                        if msg.file and msg.file.ext in ['.mp4', '.mkv', '.avi', '.mov']:
                            valid_message = msg
                            break

            if not valid_message:
                self.stdout.write(self.style.ERROR(f"No valid video or document found on Telegram for '{title}'. Aborting."))
                return

            self.stdout.write(self.style.SUCCESS("Video found on Telegram!"))

            # 2. Fetch TMDB Data
            self.stdout.write(f"Fetching TMDB data for '{title}'...")
            tmdb_data = await self.fetch_tmdb_data(title, tmdb_key)
            
            if not tmdb_data:
                self.stdout.write(self.style.ERROR(f"Could not find TMDB data for '{title}'. Aborting."))
                return

            # 3. Forward to Channel
            self.stdout.write(f"Forwarding video to your channel ({channel})...")
            channel_entity = channel if channel.startswith('@') or channel.startswith('-100') else f'@{channel}'
            
            # Instead of a simple forward, we send the media with a clean new caption
            sent_message = await client.send_message(
                channel_entity,
                file=valid_message,
                caption=tmdb_data['title_en']
            )
            
            telegram_message_id = sent_message.id
            self.stdout.write(self.style.SUCCESS(f"Forwarded successfully! Telegram Message ID: {telegram_message_id}"))

            # 4. Save to Database
            self.stdout.write(f"Saving '{title}' to database...")
            await self.save_to_db(title, tmdb_data, telegram_message_id)
            
            self.stdout.write(self.style.SUCCESS(f"Finished processing '{title}' successfully!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing '{title}': {str(e)}"))
        finally:
            await client.disconnect()

    async def fetch_tmdb_data(self, title, api_key):
        encoded_title = urllib.parse.quote(title)
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={encoded_title}&language=en-US"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as resp:
                if resp.status != 200:
                    self.stdout.write(self.style.WARNING(f"TMDB search failed with status {resp.status}"))
                    return None
                data = await resp.json()
                if not data.get('results'):
                    self.stdout.write(self.style.WARNING("No results found on TMDB."))
                    return None
                
                movie_id = data['results'][0]['id']

            # Fetch details for translations
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            
            async with session.get(f"{details_url}&language=en-US") as resp:
                data_en = await resp.json()
            
            async with session.get(f"{details_url}&language=ru-RU") as resp:
                data_ru = await resp.json()
                
            async with session.get(f"{details_url}&language=hy-AM") as resp:
                data_hy = await resp.json()

            poster_path = data_en.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else ""
            
            release_date = data_en.get('release_date', '')
            release_year = int(release_date.split('-')[0]) if release_date else 0
            
            duration = data_en.get('runtime', 0) or 0
            
            return {
                'tmdb_id': movie_id,
                'poster_url': poster_url,
                'release_year': release_year,
                'duration': duration,
                'title_en': data_en.get('title') or title,
                'description_en': data_en.get('overview', ''),
                'title_ru': data_ru.get('title') or data_en.get('title') or title,
                'description_ru': data_ru.get('overview') or data_en.get('overview', ''),
                'title_am': data_hy.get('title') or data_en.get('title') or title,
                'description_am': data_hy.get('overview') or data_en.get('overview', ''),
            }

    @sync_to_async
    def save_to_db(self, original_title, data, message_id):
        # Download poster if exists
        poster_file = None
        if data['poster_url']:
            resp = requests.get(data['poster_url'])
            if resp.status_code == 200:
                poster_file = ContentFile(resp.content, name=f"{data['tmdb_id']}_poster.jpg")

        slug = slugify(data['title_en']) + f"-{data['tmdb_id']}"
        
        movie, created = Movie.objects.update_or_create(
            tmdb_id=data['tmdb_id'],
            defaults={
                'title_en': data['title_en'],
                'title_ru': data['title_ru'],
                'title_am': data['title_am'],
                'description_en': data['description_en'],
                'description_ru': data['description_ru'],
                'description_am': data['description_am'],
                'slug': slug,
                'release_year': data['release_year'],
                'duration': data['duration'],
                'telegram_message_id': message_id,
            }
        )
        
        # Save the poster file. This replaces the old file if it exists.
        if poster_file:
            movie.poster.save(poster_file.name, poster_file, save=True)
            
        action = "Created new" if created else "Updated existing"
        self.stdout.write(f"-> {action} Movie record for '{data['title_en']}'")
