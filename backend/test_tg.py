import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeVideo
from dotenv import load_dotenv

load_dotenv()

async def get_video_duration(message):
    if not message.media:
        return 0
    if hasattr(message.media, 'document'):
        doc = message.media.document
        for attr in doc.attributes:
            if isinstance(attr, DocumentAttributeVideo):
                return attr.duration
    return 0

async def main():
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    session_string = os.environ.get('TELEGRAM_SESSION_STRING')
    
    client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
    await client.start()
    
    try:
        channel = '@hayerenfilm'
        print(f"Checking {channel}...")
        count = 0
        async for message in client.iter_messages(channel):
            if not message.media or not (hasattr(message.media, 'document') or hasattr(message.media, 'video')):
                continue
                
            duration = await get_video_duration(message)
            raw_title = message.message or ''
            
            if not raw_title and hasattr(message.media, 'document'):
                for attr in message.media.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name:
                        raw_title = attr.file_name
                        break
            
            print(f"[FOUND MEDIA] ID: {message.id}, Title: {raw_title}, Duration: {duration}s")
            
            count += 1
            if count >= 10:
                break
    finally:
        await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
