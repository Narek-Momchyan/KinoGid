import django_filters
from .models import Movie
from header.models import Category

class MovieFilter(django_filters.FilterSet):
    min_year = django_filters.NumberFilter(field_name="release_year", lookup_expr='gte')
    max_year = django_filters.NumberFilter(field_name="release_year", lookup_expr='lte')
    category_slug = django_filters.ModelMultipleChoiceFilter(
        field_name='categories__slug',
        to_field_name='slug',
        queryset=Category.objects.all(),
    )
    tmdb_id = django_filters.NumberFilter(field_name="tmdb_id")
    is_series = django_filters.BooleanFilter(field_name="is_series")

    class Meta:
        model = Movie
        fields = ['min_year', 'max_year', 'category_slug', 'tmdb_id', 'is_series']
