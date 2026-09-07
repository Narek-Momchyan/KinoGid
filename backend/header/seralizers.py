from rest_framework import serializers
from .models import Language,Navbar,Category,Logo

class LogoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logo
        fields = '__all__'
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'
class CategorySerializer(serializers.ModelSerializer):
    href = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_href(self, obj):
        if obj.href:
            return obj.href
        return f"/category/{obj.slug}"
from django.db.models import Count

class NavbarSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Navbar
        fields = ['id', 'title', 'slug', 'lang', 'href', 'order', 'categories']

    def get_categories(self, obj):
        request = self.context.get('request')
        lang = request.query_params.get('lang', obj.lang) if request else obj.lang
        cats = obj.categories.filter(lang=lang).annotate(movie_count=Count('movies')).order_by('-movie_count')
        return CategorySerializer(cats, many=True).data

