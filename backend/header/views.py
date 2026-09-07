from django.shortcuts import render
from rest_framework  import viewsets
from .models import Language,Navbar,Category,Logo
from .seralizers import LanguageSerializer,NavbarSerializer,CategorySerializer,LogoSerializer
from django.db.models import Count
class LogoViewSets(viewsets.ModelViewSet):
    queryset = Logo.objects.all()
    serializer_class = LogoSerializer

class LanguageViewset(viewsets.ModelViewSet):
   queryset = Language.objects.all()
   serializer_class = LanguageSerializer

class NavbarViewset(viewsets.ModelViewSet):
    queryset = Navbar.objects.all()
    serializer_class = NavbarSerializer
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)



class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(movie_count=Count('movies')).order_by('-movie_count')
    serializer_class = CategorySerializer
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)