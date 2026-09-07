from django.contrib import admin
from .models import Movie, Actor,HomePageMovies,RawMovie
from header.models import Category, Navbar

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_am', 'name_ru')
    search_fields = ('name_en', 'name_am', 'name_ru')

@admin.action(description='Ավելացնել «Հայերեն թարգմանված» կատեգորիան')
def add_armenian_dub_category(modeladmin, request, queryset):
    try:
        movies_navbar = Navbar.objects.get(slug='movies', lang='am')
    except:
        movies_navbar = None
        
    dub_cat, _ = Category.objects.get_or_create(
        slug="armenian dub",
        lang='am',
        defaults={
            'name': "Հայերեն թարգմանությամբ",
            'navbar': movies_navbar
        }
    )
    
    for movie in queryset:
        movie.categories.add(dub_cat)
        
    modeladmin.message_user(request, f"Successfully added category to {queryset.count()} movies.")

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title_am', 'telegram_message_id', 'release_year', 'created_at')
    list_editable = ('telegram_message_id',)
    search_fields = ('title_am', 'title_ru', 'title_en', 'slug')
    filter_horizontal = ('categories', 'actors')
    actions = [add_armenian_dub_category]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if obj.is_series and obj.tmdb_id:
            # Sync all common series fields and M2M to other episodes
            other_episodes = Movie.objects.filter(
                tmdb_id=obj.tmdb_id,
                is_series=True
            ).exclude(id=obj.id)
            
            # Update fields
            other_episodes.update(
                poster=obj.poster.name if obj.poster else '',
                description_am=obj.description_am,
                description_ru=obj.description_ru,
                description_en=obj.description_en,
                release_year=obj.release_year,
                duration=obj.duration
            )
            
            # Update M2M relations
            category_ids = list(obj.categories.values_list('id', flat=True))
            actor_ids = list(obj.actors.values_list('id', flat=True))
            
            for ep in other_episodes:
                ep.categories.set(category_ids)
                ep.actors.set(actor_ids)

admin.site.register(HomePageMovies)



@admin.register(RawMovie)
class RawMovieAdmin(admin.ModelAdmin):
    list_display = ('telegram_message_id', 'source_channel', 'is_processed', 'manual_tmdb_id', 'manual_is_tv', 'created_at')
    list_editable = ('manual_tmdb_id', 'manual_is_tv', 'is_processed')
    search_fields = ('original_caption',)
    list_filter = ('is_processed', 'source_channel', 'manual_is_tv')