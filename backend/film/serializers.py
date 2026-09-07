from rest_framework import serializers
from header.models import Category
from header.seralizers import CategorySerializer
from .models import Movie, Actor, HomePageMovies

import requests
from django.core.files.base import ContentFile


class homePageImgSeralizers(serializers.ModelSerializer):
    class Meta:
        model = HomePageMovies
        fields = '__all__'
        
class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name_am', 'name_ru', 'name_en', 'photo']

class MovieSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    category_slugs = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    poster = serializers.CharField(required=False)

    class Meta:
        model = Movie
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        # Fallback for episodes missing posters
        if not instance.poster or not instance.poster.name:
            if instance.is_series and instance.tmdb_id:
                parent = Movie.objects.filter(tmdb_id=instance.tmdb_id, is_series=True).exclude(poster='').first()
                if parent and parent.poster and parent.poster.name:
                    request = self.context.get('request')
                    if request:
                        ret['poster'] = request.build_absolute_uri(parent.poster.url)
                    else:
                        ret['poster'] = parent.poster.url
        return ret

    def create(self, validated_data):
        category_slugs = validated_data.pop('category_slugs', [])
        poster_url = validated_data.pop('poster', None)
        
        movie = Movie.objects.create(**validated_data)
        
        if poster_url and poster_url.startswith('http'):
            try:
                response = requests.get(poster_url)
                if response.status_code == 200:
                    movie.poster.save(f"{movie.slug}.jpg", ContentFile(response.content), save=True)
            except Exception:
                pass
                
        if category_slugs:
            categories = Category.objects.filter(slug__in=category_slugs, lang='am')
            movie.categories.set(categories)
            
        return movie
