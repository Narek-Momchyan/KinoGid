from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NewsPost, NewsComment
from .serializers import NewsPostSerializer, NewsCommentSerializer

class NewsPostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsPost.objects.all()
    serializer_class = NewsPostSerializer

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        news_post = self.get_object()
        author_name = request.data.get('author_name')
        text = request.data.get('text')
        
        if not author_name or not text:
            return Response({'error': 'author_name and text are required'}, status=400)
            
        comment = NewsComment.objects.create(
            news_post=news_post,
            author_name=author_name,
            text=text
        )
        return Response(NewsCommentSerializer(comment).data, status=201)
