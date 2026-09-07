from django.contrib import admin
from .models import NewsPost, NewsComment


class NewsCommentInline(admin.TabularInline):
    model = NewsComment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'generated_by_ai', 'created_at')
    list_filter = ('generated_by_ai', 'created_at')
    search_fields = ('title', 'content')
    readonly_fields = ('created_at',)
    inlines = [NewsCommentInline]


@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'news_post', 'text_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('author_name', 'text')
    readonly_fields = ('created_at',)
    list_select_related = ('news_post',)

    def text_preview(self, obj):
        return obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
    text_preview.short_description = 'Comment Preview'
