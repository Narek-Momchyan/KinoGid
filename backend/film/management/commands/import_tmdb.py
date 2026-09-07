import os
import requests
import time
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from film.models import Movie
from header.models import Category, Navbar
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Command(BaseCommand):
    help = 'Import popular and specific movies from TMDB'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('TMDB_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('TMDB_API_KEY is not set in .env'))
            return

        # Specific movies to search and import
        specific_movies = [
            "The Matrix",
            "Inception",
            "Interstellar",
            "The Dark Knight",
            "Pulp Fiction"
        ]

        # Fetch Genres map
        self.stdout.write('Fetching genres from TMDB...')
        genres_url = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}&language=en-US'
        response = requests.get(genres_url)
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch genres'))
            return
            
        genre_mapping = {g['id']: g['name'] for g in response.json().get('genres', [])}
        
        # Ensure at least one Navbar exists for categories
        navbar, _ = Navbar.objects.get_or_create(
            slug='movies',
            lang='en',
            defaults={'title': 'Movies', 'href': '/movies', 'order': 1}
        )

        movies_to_process = []

        # 1. Fetch 5 pages of Popular Movies (approx 100 movies)
        self.stdout.write('Fetching 5 pages of popular movies from TMDB...')
        for page in range(1, 6):
            movies_url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page={page}'
            response = requests.get(movies_url)
            if response.status_code == 200:
                movies_to_process.extend(response.json().get('results', []))
            time.sleep(0.1) # Small delay to respect rate limits

        # 2. Search and add Specific Movies
        self.stdout.write(f'Searching for specific movies: {", ".join(specific_movies)}...')
        for title in specific_movies:
            search_url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&language=en-US&query={title}&page=1'
            response = requests.get(search_url)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    # Take the first best match
                    movies_to_process.append(results[0])
            time.sleep(0.1)

        # Remove duplicates based on TMDB ID
        unique_movies = {}
        for item in movies_to_process:
            if item.get('id'):
                unique_movies[item['id']] = item
        
        movies_to_process = list(unique_movies.values())

        count = 0
        for item in movies_to_process:
            title = item.get('title') or item.get('original_title')
            if not title:
                continue
                
            slug = slugify(title)
            tmdb_id = item.get('id')
            slug = f"{slug}-{tmdb_id}"
                
            self.stdout.write(f'Processing: {title}')
            
            release_date = item.get('release_date', '')
            release_year = int(release_date.split('-')[0]) if release_date else 2024
            overview = item.get('overview', '')
            
            # Placeholder Video URL
            video_url = f"https://www.youtube.com/embed/dQw4w9WgXcQ"
            
            movie, created = Movie.objects.update_or_create(
                slug=slug,
                defaults={
                    'title_en': title,
                    'title_am': title,
                    'title_ru': title,
                    'description_en': overview,
                    'description_am': overview,
                    'description_ru': overview,
                    'release_year': release_year,
                    'duration': 120, 
                    'video_url': video_url,
                }
            )
            
            # Handle Poster
            poster_path = item.get('poster_path')
            if poster_path and (not movie.poster or created):
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                img_response = requests.get(poster_url)
                if img_response.status_code == 200:
                    file_name = f"{slug}.jpg"
                    movie.poster.save(file_name, ContentFile(img_response.content), save=True)
                    
            # Handle Categories
            genre_ids = item.get('genre_ids', [])
            for g_id in genre_ids:
                g_name = genre_mapping.get(g_id)
                if g_name:
                    category_slug = slugify(g_name)
                    category, _ = Category.objects.get_or_create(
                        slug=category_slug,
                        lang='en',
                        defaults={
                            'name': g_name,
                            'navbar': navbar,
                            'href': f'/category/{category_slug}'
                        }
                    )
                    movie.categories.add(category)
            count += 1
                    
        self.stdout.write(self.style.SUCCESS(f'Successfully imported/updated {count} movies!'))
