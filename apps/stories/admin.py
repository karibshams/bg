from django.contrib import admin
from .models import Story

@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'author_name', 'read_time', 'is_featured', 'published_at')
    list_filter = ('is_featured', 'published_at', 'destination')
    search_fields = ('title', 'bangla_title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured',)
