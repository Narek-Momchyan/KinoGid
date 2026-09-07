from django.db import models
from header.models import Category


class HomePageMovies(models.Model):
    images= models.FileField( upload_to='HomePageMovies/', max_length=1000, blank=True, null=True)
    video = models.FileField( upload_to='HomePageMovies/', max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"Գլխավոր էջի ֆիլմեր {self.id}"
    

class Actor(models.Model):
    name_am = models.CharField(max_length=255, verbose_name="Անուն (Հայերեն)", blank=True, null=True)
    name_ru = models.CharField(max_length=255, verbose_name="Անուն (Ռուսերեն)", blank=True, null=True)
    name_en = models.CharField(max_length=255, verbose_name="Անուն (Անգլերեն)")
    photo = models.ImageField(upload_to='actors/', verbose_name="Նկար", blank=True, null=True)

    class Meta:
        verbose_name = "Դերասան"
        verbose_name_plural = "Դերասաններ"
        ordering = ['name_en']

    def __str__(self):
        return self.name_en or self.name_am or self.name_ru

class Movie(models.Model):
    title_am = models.CharField(max_length=255, verbose_name="Վերնագիր (Հայերեն)")
    title_ru = models.CharField(max_length=255, verbose_name="Վերնագիր (Ռուսերեն)")
    title_en = models.CharField(max_length=255, verbose_name="Վերնագիր (Անգլերեն)")
    
    description_am = models.TextField(verbose_name="Նկարագրություն (Հայերեն)")
    description_ru = models.TextField(verbose_name="Նկարագրություն (Ռուսերեն)")
    description_en = models.TextField(verbose_name="Նկարագրություն (Անգլերեն)")
    
    slug = models.SlugField(unique=True, max_length=255)
    tmdb_id = models.IntegerField(verbose_name="TMDB ID", null=True, blank=True)
    
    is_series = models.BooleanField(default=False, verbose_name="Սերիալ")
    season_number = models.IntegerField(null=True, blank=True, verbose_name="Սեզոն")
    episode_number = models.IntegerField(null=True, blank=True, verbose_name="Սերիա")
    
    poster = models.FileField(upload_to='posters/', verbose_name="Պոստեր")
    telegram_message_id = models.IntegerField(
        verbose_name="Telegram Message ID",
        help_text="The exact message ID of the video in the Telegram channel",
        null=True,
        blank=True
    )
    video_url = models.URLField(verbose_name="Վիդեոյի հղում", max_length=1000, blank=True, null=True)
    
    release_year = models.PositiveIntegerField(verbose_name="Թողարկման տարեթիվ")
    duration = models.PositiveIntegerField(verbose_name="Տևողություն (րոպե)")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Դիտումների քանակ")
    
    categories = models.ManyToManyField(Category, related_name='movies', verbose_name="Կատեգորիաներ")
    actors = models.ManyToManyField(Actor, related_name='movies', verbose_name="Դերասաններ", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ստեղծման ամսաթիվ")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ֆիլմ"
        verbose_name_plural = "Ֆիլմեր"

    def __str__(self):
        return self.title_en

class RawMovie(models.Model):
    original_caption = models.TextField(verbose_name="Original Caption", blank=True, null=True)
    telegram_message_id = models.IntegerField(verbose_name="Telegram Message ID", unique=True)
    source_channel = models.CharField(max_length=255, verbose_name="Source Channel")
    is_processed = models.BooleanField(default=False, verbose_name="Is Processed")
    manual_tmdb_id = models.IntegerField(null=True, blank=True, verbose_name="Manual TMDB ID", help_text="Paste TMDB ID here to force the exact movie/TV show.")
    manual_is_tv = models.BooleanField(default=False, null=True, blank=True, verbose_name="Manual is TV?", help_text="Check this if the manual_tmdb_id is for a TV show.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Raw Movie"
        verbose_name_plural = "Raw Movies"
        ordering = ['-created_at']

    def __str__(self):
        return f"RawMovie {self.telegram_message_id} from {self.source_channel}"
