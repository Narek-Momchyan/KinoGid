from django.core.management.base import BaseCommand
from film.models import Movie
from header.models import Category, Navbar


class Command(BaseCommand):
    help = 'Retroactively adds the "Սerialner" category to all movies marked as is_series=True.'

    def handle(self, *args, **options):
        try:
            movies_navbar = Navbar.objects.get(slug='movies', lang='am')
        except:
            movies_navbar = None

        tv_cat, _ = Category.objects.get_or_create(
            name="Սերիալներ",
            lang='am',
            defaults={
                'slug': 'tv-series',
                'navbar': movies_navbar
            }
        )

        # Find all movies that are series but DON'T have the TV category
        series_movies = Movie.objects.filter(is_series=True)
        count = series_movies.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("No series found in the database."))
            return

        added = 0
        for movie in series_movies:
            if not movie.categories.filter(id=tv_cat.id).exists():
                movie.categories.add(tv_cat)
                added += 1
                self.stdout.write(f"  Tagged: {movie.title_am or movie.title_en}")

        self.stdout.write(self.style.SUCCESS(f"\nDone! Added 'Սerialner' category to {added} movies out of {count} total series."))
