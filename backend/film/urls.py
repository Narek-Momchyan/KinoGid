from django.urls import path, include
from rest_framework.routers import DefaultRouter, APIRootView
from .views import MovieViewSet, stream_telegram_video, homePageImgSeralizers

class CustomAPIRootView(APIRootView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Add the header link manually
        response.data['header'] = request.build_absolute_uri('/api/header/')
        return response

class CustomRouter(DefaultRouter):
    APIRootView = CustomAPIRootView

router = CustomRouter()
router.register(r'movies', MovieViewSet, basename='movie')
router.register(r'homepage-movies', homePageImgSeralizers, basename='homepage-movie')

urlpatterns = [
    path('', include(router.urls)),
    path('stream/<int:movie_id>/', stream_telegram_video, name='stream_telegram_video'),
]

