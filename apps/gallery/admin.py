from django.contrib import admin
from .models import GalleryItem

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'destination', 'tour', 'is_featured', 'order', 'created_at')
    list_filter = ('category', 'is_featured', 'destination')
    search_fields = ('title', 'bangla_title', 'caption', 'bangla_caption')
    list_editable = ('is_featured', 'order')
    autocomplete_fields = ('destination', 'tour')
