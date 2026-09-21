from django.db import models
from django.core.exceptions import ValidationError

class SiteSetting(models.Model):
    """
    Singleton model for global site branding, hero text, contact info,
    and trust statistics displayed across the website.
    """
    site_name = models.CharField(max_length=100, default="ভ্রমণঘুড়ি (Bhromonghuri)")
    site_tagline_bn = models.CharField(max_length=200, default="নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি")
    site_tagline_en = models.CharField(max_length=200, default="Explore • Experience • Discover")
    hero_headline = models.CharField(max_length=255, default="অদেখা বাংলাকে নতুন চোখে দেখা")
    hero_subheadline = models.TextField(default="ভ্রমণঘুড়ির সাথে আবিষ্কার করুন পাহাড়, সমুদ্র, মেঘের দেশ আর সবুজ বনানীর অপূর্ব সৌন্দর্য। প্রতিটি পদক্ষেপে নিরাপদ ও রোমাঞ্চকর ভ্রমণ।")
    
    phone = models.CharField(max_length=60, default="+8801518919370, 01855939459")
    email = models.EmailField(default="bhromonghuri@gmail.com")
    address = models.CharField(max_length=255, default="Dhaka, Bangladesh")
    bkash_number = models.CharField(max_length=100, default="01518919370 (Personal / Send Money)")
    nagad_number = models.CharField(max_length=100, default="01855939459 (Personal / Send Money)")
    
    facebook_url = models.URLField(blank=True, default="https://www.facebook.com/share/g/19km9RqB1g/")
    instagram_url = models.URLField(blank=True, default="https://instagram.com/bhromonghuri")
    youtube_url = models.URLField(blank=True, default="https://youtube.com/@bhromonghuri")
    
    # Trust statistics displayed on homepage
    total_tours_count = models.CharField(max_length=20, default="50+")
    total_travelers_count = models.CharField(max_length=20, default="1,500+")
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    destinations_count = models.CharField(max_length=20, default="25+")

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern: always keep id=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"{self.site_name} Settings"


class Testimonial(models.Model):
    """Customer reviews and feedback displayed on the homepage."""
    customer_name = models.CharField(max_length=120)
    customer_designation = models.CharField(max_length=120, blank=True, help_text="e.g. Travel Enthusiast or Software Engineer")
    tour_name = models.CharField(max_length=150, help_text="e.g. Sajek Valley Tour")
    avatar = models.ImageField(upload_to='testimonials/avatars/', blank=True, null=True)
    review = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5, choices=[(i, f"{i} Stars") for i in range(1, 6)])
    is_featured = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.customer_name} - {self.tour_name} ({self.rating}★)"


class FAQ(models.Model):
    """Frequently Asked Questions."""
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question
