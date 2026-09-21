from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from apps.tours.models import Destination

class Story(models.Model):
    """Travel stories, blogs, and expedition journals."""
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Approval'),
        (STATUS_APPROVED, 'Approved / Published'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    bangla_title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories')
    
    author_name = models.CharField(max_length=120, default="ভ্রমণঘুড়ি টিম")
    author_email = models.EmailField(blank=True, null=True, help_text="Author email for notifications/contact")
    read_time = models.CharField(max_length=50, default="4 min read")
    cover_image = models.ImageField(upload_to='stories/covers/', blank=True, null=True)
    excerpt = models.TextField(blank=True, help_text="Short teaser for story cards")
    content = models.TextField(help_text="Full story / travel guide article")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_APPROVED)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Travel Story"
        verbose_name_plural = "Travel Stories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or f"story-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            candidate = base_slug
            num = 1
            while Story.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{num}"
                num += 1
            self.slug = candidate
        if not self.excerpt and self.content:
            self.excerpt = self.content[:220] + ('...' if len(self.content) > 220 else '')
        super().save(*args, **kwargs)

    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class StoryImage(models.Model):
    """Multiple photo uploads attached to a travel story (up to 10 photos)."""
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='stories/photos/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at', 'id']
        verbose_name = "Story Photo"
        verbose_name_plural = "Story Photos"

    def __str__(self):
        return f"Photo for {self.story.title}"
