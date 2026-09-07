from rest_framework import serializers
from .models import NewsPost, NewsComment

class NewsCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsComment
        fields = ['id', 'author_name', 'text', 'created_at']

class NewsPostSerializer(serializers.ModelSerializer):
    comments = NewsCommentSerializer(many=True, read_only=True)

    class Meta:
        model = NewsPost
        fields = ['id', 'title', 'content', 'image_url', 'created_at', 'generated_by_ai', 'comments']
