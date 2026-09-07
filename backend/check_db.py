import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base.settings')
django.setup()

from film.models import Movie

count = Movie.objects.count()
print(f'Movies count: {count}')

last = Movie.objects.last()
if last:
    print(f'Last movie added: {last.title_en} / {last.title_am}')
else:
    print('No movies in database yet.')
