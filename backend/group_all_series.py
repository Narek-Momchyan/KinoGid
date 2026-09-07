import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kino_project.settings')
django.setup()

from film.models import Movie
from collections import defaultdict
import re

def group_series():
    series_movies = Movie.objects.filter(is_series=True)
    
    # Group by a normalized title (stripping out "Episode X" and punctuation)
    groups = defaultdict(list)
    
    for movie in series_movies:
        title = movie.title_en or movie.title_am or movie.title_ru or ""
        
        # Remove "Episode X", "Season X", etc
        base_title = re.sub(r'(?i)Episode\s*\d+.*$', '', title)
        base_title = re.sub(r'(?i)Series.*$', '', base_title)
        base_title = re.sub(r'[:\-]', '', base_title).strip().lower()
        
        if not base_title:
            continue
            
        groups[base_title].append(movie)
        
    updated = 0
    for base_title, movies in groups.items():
        if len(movies) <= 1:
            continue
            
        # Find the best tmdb_id to use (prefer positive real ones)
        best_tmdb_id = None
        for m in movies:
            if m.tmdb_id and m.tmdb_id > 0:
                best_tmdb_id = m.tmdb_id
                break
                
        if not best_tmdb_id:
            # If all are negative, just use the first one's ID for all of them
            best_tmdb_id = movies[0].tmdb_id
            
        print(f"Grouping '{base_title}' ({len(movies)} episodes) under TMDB ID {best_tmdb_id}")
        
        for m in movies:
            if m.tmdb_id != best_tmdb_id:
                m.tmdb_id = best_tmdb_id
                m.save(update_fields=['tmdb_id'])
                updated += 1
                
    print(f"Done! Updated {updated} episodes to properly group them.")

if __name__ == '__main__':
    group_series()
