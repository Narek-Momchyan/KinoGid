from django.urls import path
from .views import ai_advisor_view

urlpatterns = [
    path('', ai_advisor_view, name='ai_advisor'),
]
