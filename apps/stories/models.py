from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from apps.tours.models import Destination

class Story(models.Model):
    """Travel stories, blogs, and expedition journals."""
    title = models.CharField(max_length=255)
    bangla_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories')
    
    author_name = models.CharField(max_length=120, default="ভ্রমণঘুড়ি টিম")
    read_time = models.CharField(max_length=50, default="4 min read")
    cover_image = models.ImageField(upload_to='stories/covers/', blank=True, null=True)
    excerpt = models.TextField(help_text="Short teaser for story cards")
    content = models.TextField(help_text="Full story / travel guide article")
    
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Travel Story"
        verbose_name_plural = "Travel Stories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
