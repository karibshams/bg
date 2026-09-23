from django.db import models
from apps.tours.models import Destination

class GalleryItem(models.Model):
    """Curated travel photograph or album highlight."""
    CATEGORY_CHOICES = [
        ('ALL', 'All Photos'),
        ('MOUNTAIN', 'Mountains & Hills (পাহাড়)'),
        ('BEACH', 'Beaches & Islands (সমুদ্র)'),
        ('FOREST', 'Forests & Lakes (বন ও হাওর)'),
        ('CULTURE', 'Culture & Local Life (ঐতিহ্য)'),
        ('GROUP', 'Travelers & Moments (স্মৃতি)'),
    ]

    title = models.CharField(max_length=200)
    bangla_title = models.CharField(max_length=200, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_items')
    tour = models.ForeignKey('tours.Tour', on_delete=models.SET_NULL, null=True, blank=True, related_name='gallery_items')
    image = models.ImageField(upload_to='gallery/photos/')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='MOUNTAIN')
    
    caption = models.CharField(max_length=255, blank=True)
    bangla_caption = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=True, help_text="Show on homepage gallery preview")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
