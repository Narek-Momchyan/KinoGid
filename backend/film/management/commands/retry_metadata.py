from django.core.management.base import BaseCommand
from django.db.models import Q
from film.models import Movie, RawMovie

class Command(BaseCommand):
    help = "Reset incomplete movies to be reprocessed by process_raw_movies."

    def handle(self, *args, **options):
        # Find movies with missing tmdb_id or empty poster
        incomplete_movies = Movie.objects.filter(
            Q(tmdb_id__isnull=True) | Q(poster='') | Q(poster__isnull=True)
        )
        
        count = 0
        for movie in incomplete_movies:
            if movie.telegram_message_id:
                try:
                    # Find the corresponding raw movie using telegram_message_id
                    raw_movie = RawMovie.objects.get(telegram_message_id=movie.telegram_message_id)
                    
                    # Reset its processed status so the scraper picks it up again
                    raw_movie.is_processed = False
                    raw_movie.save()
                    
                    # Delete the incomplete movie shell
                    movie.delete()
                    count += 1
                except RawMovie.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"RawMovie not found for telegram_message_id {movie.telegram_message_id}"))
            else:
                # If there's no telegram_message_id, we can't link it back to a raw movie safely
                self.stdout.write(self.style.WARNING(f"Movie ID {movie.id} ('{movie.title_en}') has no telegram_message_id"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully reset {count} movies. The videos are safe in RawMovie. "
            "Run `python manage.py process_raw_movies` to fetch the missing posters and translations!"
        ))
