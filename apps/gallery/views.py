from django.shortcuts import render
from .models import GalleryItem

def gallery_index_view(request):
    """
    Renders photography gallery with category filters and Alpine.js lightbox.
    """
    category = request.GET.get('category', 'ALL')
    items = GalleryItem.objects.select_related('destination').all()

    if category != 'ALL':
        items = items.filter(category=category)

    return render(request, 'gallery/index.html', {
        'items': items,
        'selected_category': category,
        'categories': GalleryItem.CATEGORY_CHOICES,
    })
