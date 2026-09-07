import os
import re
import asyncio
from django.http import StreamingHttpResponse, Http404, HttpResponse
from django.core.cache import cache
from asgiref.sync import sync_to_async
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from telethon import TelegramClient
from telethon.sessions import StringSession

from .models import Movie, HomePageMovies
from .serializers import MovieSerializer, homePageImgSeralizers
from .filters import MovieFilter
from .pagination import StandardResultsSetPagination

API_ID = int(os.environ.get('TELEGRAM_API_ID', '36363516'))
API_HASH = os.environ.get('TELEGRAM_API_HASH', '')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING', '')
CHANNEL_USERNAME = os.environ.get('TELEGRAM_CHANNEL_USERNAME', 'kino_gid_2026')

# Maximum request size allowed by Telethon's iter_download (512KB for faster first-byte)
TELETHON_CHUNK_SIZE = 512 * 1024

# Global Telegram Client to reuse connection across requests (ASGI friendly)
tg_client = None
tg_client_lock = asyncio.Lock()
tg_message_cache = {}

async def get_tg_client():
    global tg_client
    if tg_client is None:
        async with tg_client_lock:
            if tg_client is None:
                client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
                await client.connect()
                tg_client = client
    else:
        if not tg_client.is_connected():
            await tg_client.connect()
    return tg_client


async def stream_telegram_video(request, movie_id):
    try:
        # Retrieve or initialize the shared ASGI Telegram client
        client = await get_tg_client()

        try:
            movie = await Movie.objects.aget(id=movie_id)
        except Movie.DoesNotExist:
            raise Http404("Ֆիլմը բազայում չի գտնվել:")

        if not movie.telegram_message_id:
            raise Http404("Այս ֆիլմի համար Telegram Message ID առկա չէ:")

        cache_key = f"tg_media_meta_{movie.telegram_message_id}"
        meta = await sync_to_async(cache.get)(cache_key)
            
        message = tg_message_cache.get(movie.telegram_message_id)
        
        file_size = 0
        mime_type = "video/mp4"
        
        if meta:
            file_size = meta.get('file_size', 0)
            mime_type = meta.get('mime_type', 'video/mp4')
            
        if not message or not meta:
            message = await client.get_messages(CHANNEL_USERNAME, ids=movie.telegram_message_id)
            if not message or not message.media:
                raise Http404("Տեսանյութը Telegram-ում չի գտնվել:")

            # 1. EXACT RANGE PARSING
            if getattr(message, 'video', None) and getattr(message.video, 'file_size', None):
                file_size = message.video.file_size
            elif getattr(message, 'document', None) and getattr(message.document, 'file_size', None):
                file_size = message.document.file_size
            elif getattr(message, 'video', None) and getattr(message.video, 'size', None):
                file_size = message.video.size
            elif getattr(message, 'document', None) and getattr(message.document, 'size', None):
                file_size = message.document.size
            elif getattr(message, 'file', None) and getattr(message.file, 'size', None):
                file_size = message.file.size
            elif getattr(message, 'media', None) and getattr(message.media, 'document', None) and getattr(message.media.document, 'size', None):
                file_size = message.media.document.size
            else:
                file_size = 0
                
            mime_type = "video/mp4"
            if getattr(message, 'file', None) and getattr(message.file, 'mime_type', None):
                mime_type = message.file.mime_type
            elif getattr(message, 'media', None) and getattr(message.media, 'document', None) and getattr(message.media.document, 'mime_type', None):
                mime_type = message.media.document.mime_type
                
            meta = {
                'file_size': file_size,
                'mime_type': mime_type,
            }
            await sync_to_async(cache.set)(cache_key, meta, 86400)
            tg_message_cache[movie.telegram_message_id] = message

        if file_size <= 0:
            raise Http404("Տեսանյութի չափը անհայտ է:")

        # Parse HTTP_RANGE
        range_header = request.headers.get('Range') or request.META.get('HTTP_RANGE')
        start_byte = 0
        end_byte = file_size - 1

        if not range_header:
            end_byte = min((1024 * 1024 * 2) - 1, file_size - 1)
        else:
            match = re.match(r'bytes=(\d*)-(\d*)', range_header)
            if match:
                start_str = match.group(1)
                end_str = match.group(2)
                
                if start_str:
                    start_byte = int(start_str)
                
                if end_str:
                    end_byte = int(end_str)
                else:
                    end_byte = min(start_byte + (1024 * 1024 * 2) - 1, file_size - 1)

        if start_byte >= file_size:
            res = HttpResponse(status=416)
            res['Content-Range'] = f'bytes */{file_size}'
            res['Access-Control-Expose-Headers'] = 'Content-Range'
            return res

        # Calculate chunk_size
        chunk_size = (end_byte - start_byte) + 1
        if chunk_size <= 0:
            chunk_size = 1

        # 2. STRICT ASYNC GENERATOR
        async def video_chunk_generator(start_byte, chunk_size):
            bytes_yielded = 0
            
            # Let Telethon use its default valid request_size
            async for chunk in client.iter_download(message, offset=start_byte):
                # FIX: Telethon yields memoryview for unaligned offsets. Django requires bytes!
                if isinstance(chunk, memoryview):
                    chunk = bytes(chunk)
                    
                chunk_len = len(chunk)
                if bytes_yielded + chunk_len > chunk_size:
                    # Yield only the exact remaining bytes the browser asked for
                    yield chunk[:chunk_size - bytes_yielded]
                    break
                
                yield chunk
                bytes_yielded += chunk_len
                
                if bytes_yielded >= chunk_size:
                    break
            
        # 4. DEBUGGING
        print(f"Streaming request: Range={range_header}, Parsed: {start_byte}-{end_byte}, Chunk: {chunk_size}")

        # 3. STRICT RESPONSE HEADERS & CORS
        response = StreamingHttpResponse(video_chunk_generator(start_byte, chunk_size), status=206)
        response['Content-Type'] = 'video/mp4'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(chunk_size)
        response['Content-Range'] = f'bytes {start_byte}-{end_byte}/{file_size}'
        response['Cache-Control'] = 'public, max-age=86400'
        response['Access-Control-Expose-Headers'] = 'Content-Range, Accept-Ranges, Content-Length'

        return response

    except Http404:
        raise
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(err_msg)
        return HttpResponse("Internal Server Error", status=500)


class BulkCreateMixin:
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
class homePageImgSeralizers(viewsets.ModelViewSet):
    queryset=HomePageMovies.objects.all()
    serializer_class = homePageImgSeralizers

class MovieViewSet(BulkCreateMixin, viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MovieFilter

    search_fields = ['slug', 'title_am', 'title_ru', 'title_en',
                     'description_am', 'description_ru', 'description_en',
                     'actors__name_am', 'actors__name_ru', 'actors__name_en']

    ordering_fields = ['views_count', 'release_year', 'created_at']
    ordering = ['-created_at']