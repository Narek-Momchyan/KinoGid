from django.urls import path,include
from . import views
from rest_framework import routers
from .views import LogoViewSets,LanguageViewset,NavbarViewset,CategoryViewset
router = routers.DefaultRouter()
router.register(r'logos', views.LogoViewSets)
router.register(r'languages', views.LanguageViewset)
router.register(r'navbars', views.NavbarViewset)
router.register(r'categories', views.CategoryViewset)
urlpatterns = [
    path('', include(router.urls)),
]
