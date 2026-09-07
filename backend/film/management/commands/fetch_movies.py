import os
import time
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from film.models import Movie
from header.models import Category

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'

class Command(BaseCommand):
    help = 'Fetches movies from TMDB and populates the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--popular',
            action='store_true',
            help='Fetch popular movies',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of movies to fetch (default: 20)',
        )

    def handle(self, *args, **options):
        if not TMDB_API_KEY:
            self.stdout.write(self.style.ERROR('TMDB_API_KEY is not set in environment variables.'))
            return

        is_popular = options['popular']
        count = options['count']

        if is_popular:
            endpoint = f"{BASE_URL}/movie/popular"
        else:
            endpoint = f"{BASE_URL}/discover/movie"

        movies_added = 0
        movies_updated = 0
        page = 1

        self.stdout.write(self.style.SUCCESS(f"Starting fetch for {count} movies..."))

        while (movies_added + movies_updated) < count:
            params = {
                'api_key': TMDB_API_KEY,
                'page': page,
            }
            
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch page {page}: {response.text}"))
                break
                
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                break
                
            for item in results:
                if (movies_added + movies_updated) >= count:
                    break
                    
                tmdb_id = item['id']
                
                detail_url = f"{BASE_URL}/movie/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=translations,credits"
                detail_resp = requests.get(detail_url)
                
                if detail_resp.status_code != 200:
                    continue
                    
                detail_data = detail_resp.json()
                
                translations = detail_data.get('translations', {}).get('translations', [])
                
                title_en = detail_data.get('title', '')
                description_en = detail_data.get('overview', '')
                
                title_ru = title_en
                description_ru = description_en
                
                title_am = title_en
                description_am = description_en
                
                for trans in translations:
                    iso_639_1 = trans.get('iso_639_1')
                    data_trans = trans.get('data', {})
                    
                    if iso_639_1 == 'ru':
                        title_ru = data_trans.get('title') or title_ru
                        description_ru = data_trans.get('overview') or description_ru
                    elif iso_639_1 == 'hy':
                        title_am = data_trans.get('title') or title_am
                        description_am = data_trans.get('overview') or description_am
                
                # Default values
                release_year = 2024
                release_date = detail_data.get('release_date')
                if release_date:
                    try:
                        release_year = int(release_date.split('-')[0])
                    except:
                        pass
                        
                duration = detail_data.get('runtime') or 120
                
                slug = slugify(f"{title_en}-{release_year}-{tmdb_id}")
                
                # Try to find by tmdb_id first, then by slug
                try:
                    movie = Movie.objects.get(tmdb_id=tmdb_id)
                except Movie.DoesNotExist:
                    try:
                        movie = Movie.objects.get(slug=slug)
                        # Link existing movie to tmdb_id
                        movie.tmdb_id = tmdb_id
                    except Movie.DoesNotExist:
                        movie = None
                
                if movie:
                    movie.title_en = title_en
                    movie.title_ru = title_ru
                    movie.title_am = title_am
                    movie.description_en = description_en
                    movie.description_ru = description_ru
                    movie.description_am = description_am
                    movie.release_year = release_year
                    movie.duration = duration
                    movie.save()
                    created = False
                else:
                    movie = Movie.objects.create(
                        tmdb_id=tmdb_id,
                        title_en=title_en,
                        title_ru=title_ru,
                        title_am=title_am,
                        description_en=description_en,
                        description_ru=description_ru,
                        description_am=description_am,
                        slug=slug,
                        release_year=release_year,
                        duration=duration,
                        views_count=0,
                    )
                    created = True
                
                # Download poster if created or missing
                if created or not movie.poster:
                    poster_path = detail_data.get('poster_path')
                    if poster_path:
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        try:
                            img_resp = requests.get(poster_url)
                            if img_resp.status_code == 200:
                                movie.poster.save(f"{slug}.jpg", ContentFile(img_resp.content), save=True)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"Failed to download poster for {title_en}"))
                
                # Genres
                genres = detail_data.get('genres', [])
                for genre in genres:
                    cat_name = genre['name']
                    # We create EN category, and maybe we should translate it too, but let's just make it simple
                    cat, _ = Category.objects.get_or_create(
                        name=cat_name, 
                        lang='en',
                        defaults={'slug': slugify(cat_name)}
                    )
                    movie.categories.add(cat)
                
                # Actors (Cast)
                from film.models import Actor
                credits = detail_data.get('credits', {}).get('cast', [])
                for cast_member in credits[:10]:  # Top 10 actors
                    actor_name = cast_member.get('name')
                    if not actor_name: continue
                    
                    actor, actor_created = Actor.objects.get_or_create(
                        name_en=actor_name,
                        defaults={
                            'name_am': actor_name,
                            'name_ru': actor_name
                        }
                    )
                    
                    if actor_created and cast_member.get('profile_path'):
                        profile_url = f"https://image.tmdb.org/t/p/w185{cast_member['profile_path']}"
                        try:
                            p_resp = requests.get(profile_url)
                            if p_resp.status_code == 200:
                                actor.photo.save(f"{slugify(actor_name)}.jpg", ContentFile(p_resp.content), save=True)
                        except Exception:
                            pass
                            
                    movie.actors.add(actor)
                
                if created:
                    movies_added += 1
                    self.stdout.write(self.style.SUCCESS(f"Added: {title_en}"))
                else:
                    movies_updated += 1
                    self.stdout.write(self.style.WARNING(f"Updated: {title_en}"))
                    
                time.sleep(0.1)  # Respect rate limits
            
            page += 1

        self.stdout.write(self.style.SUCCESS(f"Finished! Added: {movies_added}, Updated: {movies_updated}"))
