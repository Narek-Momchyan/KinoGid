from django.core.management.base import BaseCommand
from film.models import Movie

class Command(BaseCommand):
    help = 'Syncs series data (poster, description) across all episodes'

    def handle(self, *args, **options):
        # Find all unique tmdb_ids for series
        series_ids = Movie.objects.filter(is_series=True).values_list('tmdb_id', flat=True).distinct()
        
        for tmdb_id in series_ids:
            if not tmdb_id:
                continue
                
            # Get all episodes for this series
            episodes = Movie.objects.filter(tmdb_id=tmdb_id, is_series=True)
            
            # Find the "best" episode to copy data from (the one with a poster)
            best_ep = episodes.exclude(poster='').first()
            if not best_ep:
                best_ep = episodes.first()
                
            if not best_ep:
                continue
                
            # Copy data to all other episodes
            other_episodes = episodes.exclude(id=best_ep.id)
            
            if other_episodes.exists():
                other_episodes.update(
                    poster=best_ep.poster.name if best_ep.poster else '',
                    description_am=best_ep.description_am,
                    description_ru=best_ep.description_ru,
                    description_en=best_ep.description_en,
                    release_year=best_ep.release_year,
                    duration=best_ep.duration
                )
                
                category_ids = list(best_ep.categories.values_list('id', flat=True))
                actor_ids = list(best_ep.actors.values_list('id', flat=True))
                
                for ep in other_episodes:
                    ep.categories.set(category_ids)
                    ep.actors.set(actor_ids)
                    
        self.stdout.write(self.style.SUCCESS('Successfully synced series data!'))
