from django.core.management.base import BaseCommand
from film.models import Movie, RawMovie
import re

class Command(BaseCommand):
    help = 'Groups series episodes by assigning them the same tmdb_id based on their name'

    def handle(self, *args, **options):
        # We will assign negative TMDB IDs starting from -1000 for local grouping
        # Dictionary to map 'Normalized Series Name' -> tmdb_id
        series_map = {}
        next_local_id = -1000

        # Fetch all series movies
        series_movies = Movie.objects.filter(is_series=True)
        self.stdout.write(f"Found {series_movies.count()} episodes marked as series.")

        for movie in series_movies:
            if movie.tmdb_id and movie.tmdb_id > 0:
                # Keep valid TMDB IDs
                continue

            # Try to get the original caption
            raw = RawMovie.objects.filter(telegram_message_id=movie.telegram_message_id).first()
            if not raw:
                continue

            caption = raw.original_caption or ""
            
            # Use regex to extract the series name before the season/episode part
            # Look for markers like "Սեզոն", "Սերիա", "Մաս", or the | symbol
            # Usually format is: Series Name | Սեզոն 1 ... or Series Name (Սերիա 3)
            
            name = movie.title_en or movie.title_am
            
            # Simple heuristic: Split by '|', '(', 'Սեզոն', 'Սերիա'
            for delimiter in ['|', '(', 'Սեզոն', 'Սերիա', 'սեզոն', 'սերիա']:
                if delimiter in name:
                    name = name.split(delimiter)[0]
                    
            name = name.strip()
            if not name:
                name = "Unknown Series"

            # Check if this name is already mapped
            if name not in series_map:
                series_map[name] = next_local_id
                next_local_id -= 1

            # Update the movie's tmdb_id
            movie.tmdb_id = series_map[name]
            movie.save()

        self.stdout.write(self.style.SUCCESS('Successfully grouped series!'))
