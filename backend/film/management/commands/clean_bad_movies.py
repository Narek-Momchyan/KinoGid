from django.core.management.base import BaseCommand
from film.models import Movie, RawMovie

class Command(BaseCommand):
    help = 'Finds and deletes corrupted movies using Python-level evaluation, reverting their RawMovies to unprocessed.'

    def handle(self, *args, **options):
        self.stdout.write("Scanning all movies for corruption...")
        
        all_movies = Movie.objects.all()
        
        deleted_count = 0
        reverted_count = 0
        
        for movie in all_movies:
            is_bad = False
            
            # Check for completely empty titles or whitespace
            if not movie.title_am or str(movie.title_am).strip() == "":
                is_bad = True
            elif not movie.title_en or str(movie.title_en).strip() == "":
                is_bad = True
            elif not movie.title_ru or str(movie.title_ru).strip() == "":
                is_bad = True
                
            # Check for completely empty descriptions or whitespace
            elif not movie.description_am or str(movie.description_am).strip() == "":
                is_bad = True
            elif not movie.description_en or str(movie.description_en).strip() == "":
                is_bad = True
            elif not movie.description_ru or str(movie.description_ru).strip() == "":
                is_bad = True
                
            # Check for missing poster/image
            elif not movie.poster or not movie.poster.name:
                is_bad = True
                
            # Check for corrupted keywords in titles
            else:
                for bad in ["error 500", "server error", "that's an error", "անհայտ"]:
                    if bad in str(movie.title_am).lower() or \
                       bad in str(movie.title_en).lower() or \
                       bad in str(movie.title_ru).lower():
                        is_bad = True
                        break
                        
            if is_bad:
                # 4. Find the linked RawMovie and revert
                if movie.telegram_message_id:
                    raw_movie = RawMovie.objects.filter(telegram_message_id=movie.telegram_message_id).first()
                    if raw_movie:
                        raw_movie.is_processed = False
                        raw_movie.save()
                        reverted_count += 1
                        
                title_to_print = movie.title_en or movie.title_am or "EMPTY TITLE"
                self.stdout.write(self.style.WARNING(f"Deleting bad movie: {title_to_print} (ID: {movie.id})"))
                
                # Delete the bad movie object
                movie.delete()
                deleted_count += 1
                
        if deleted_count == 0:
            self.stdout.write(self.style.SUCCESS("Database is clean! No corrupted movies found."))
        else:
            self.stdout.write(self.style.SUCCESS(f"\nCleanup Complete!"))
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} corrupted movies and reverted their RawMovies."))
