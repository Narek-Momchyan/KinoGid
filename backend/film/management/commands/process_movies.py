import os
import asyncio
import urllib.parse
from pathlib import Path
import aiohttp
import requests

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from asgiref.sync import sync_to_async
from film.models import Movie
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

load_dotenv()

class Command(BaseCommand):
    help = 'Scans movies_to_upload/ directory, uploads to Telegram, fetches TMDB data, and saves to DB.'

    def handle(self, *args, **options):
        # Run the async main function
        try:
            asyncio.run(self.process_all())
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Process interrupted by user."))

    async def process_all(self):
        # Ensure the upload directory exists in the base dir (project root or backend root)
        # Assuming we run this from backend directory
        upload_dir = Path('movies_to_upload')
        if not upload_dir.exists():
            upload_dir.mkdir(parents=True)
            self.stdout.write(self.style.WARNING("Created movies_to_upload/ directory. Please add .mp4/.mkv files and run again."))
            return

        movie_files = list(upload_dir.glob('*.mp4')) + list(upload_dir.glob('*.mkv'))
        
        if not movie_files:
            self.stdout.write(self.style.WARNING("No .mp4 or .mkv files found in movies_to_upload/"))
            return

        api_id = os.environ.get('TELEGRAM_API_ID')
        api_hash = os.environ.get('TELEGRAM_API_HASH')
        session_string = os.environ.get('TELEGRAM_SESSION_STRING')
        channel = os.environ.get('TELEGRAM_CHANNEL')
        tmdb_key = os.environ.get('TMDB_API_KEY')
        
        if not all([api_id, api_hash, session_string, channel, tmdb_key]):
            self.stdout.write(self.style.ERROR("Missing required environment variables (TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_STRING, TELEGRAM_CHANNEL, TMDB_API_KEY)."))
            return

        # Initialize Telethon Client
        client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
        self.stdout.write("Connecting to Telegram...")
        await client.start()

        for file_path in movie_files:
            title = file_path.stem  # Filename without extension
            self.stdout.write(self.style.SUCCESS(f"\n--- Processing: {title} ---"))

            try:
                # 1. Fetch TMDB Data FIRST so we don't upload if it fails
                self.stdout.write(f"Fetching TMDB data for '{title}'...")
                tmdb_data = await self.fetch_tmdb_data(title, tmdb_key)
                
                if not tmdb_data:
                    self.stdout.write(self.style.ERROR(f"Could not find TMDB data for {title}. Skipping this movie."))
                    continue

                # 2. Upload to Telegram
                self.stdout.write(f"Uploading '{file_path.name}' to Telegram... (This may take a while)")
                
                channel_entity = channel if channel.startswith('@') or channel.startswith('-100') else f'@{channel}'
                
                message = await client.send_file(
                    channel_entity,
                    str(file_path),
                    caption=tmdb_data['title_en'],
                    supports_streaming=True
                )
                
                telegram_message_id = message.id
                self.stdout.write(self.style.SUCCESS(f"Uploaded successfully! Telegram Message ID: {telegram_message_id}"))

                # 3. Save to Database
                self.stdout.write(f"Saving '{title}' to database...")
                await self.save_to_db(title, tmdb_data, telegram_message_id)

                # 4. Cleanup
                self.stdout.write(f"Deleting local file: {file_path.name}")
                os.remove(file_path)
                self.stdout.write(self.style.SUCCESS(f"Finished processing '{title}' successfully!"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing '{title}': {str(e)}"))

        await client.disconnect()
        self.stdout.write(self.style.SUCCESS("\nAll movies processed!"))

    async def fetch_tmdb_data(self, title, api_key):
        # We need to search by title
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

            # Fetch details for the languages
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            
            # Fetch EN
            async with session.get(f"{details_url}&language=en-US") as resp:
                data_en = await resp.json()
            
            # Fetch RU
            async with session.get(f"{details_url}&language=ru-RU") as resp:
                data_ru = await resp.json()
                
            # Fetch HY (Armenian might not be fully supported by TMDB, so we fallback)
            async with session.get(f"{details_url}&language=hy-AM") as resp:
                data_hy = await resp.json()

            poster_path = data_en.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else ""
            
            release_date = data_en.get('release_date', '')
            release_year = int(release_date.split('-')[0]) if release_date else 0
            
            duration = data_en.get('runtime', 0) or 0
            
            # Fallback logic for title and overview
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
