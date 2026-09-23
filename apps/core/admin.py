from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSetting, Testimonial, FAQ, EmailVerification

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'email', 'destinations_count', 'total_tours_count', 'total_travelers_count')
    fieldsets = (
        ('Branding & Hero', {
            'fields': ('site_name', 'site_tagline_bn', 'site_tagline_en', 'hero_headline', 'hero_subheadline')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Social Links', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url')
        }),
        ('Key Trust Statistics', {
            'fields': ('total_tours_count', 'total_travelers_count', 'average_rating', 'destinations_count'),
            'description': 'These numbers appear in the "Why Travel With Us" section on the homepage.'
        }),
    )

    def has_add_permission(self, request):
        # Only allow 1 instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'tour_name', 'rating_stars', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'rating', 'created_at')
    search_fields = ('customer_name', 'tour_name', 'review')
    list_editable = ('is_featured',)

    def rating_stars(self, obj):
        return format_html('<span style="color: #f59e0b; font-weight: bold;">{}★</span>', obj.rating)
    rating_stars.short_description = "Rating"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('question', 'answer')


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'otp_code', 'purpose', 'is_used', 'expires_at', 'created_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('email', 'user__username', 'otp_code')
    readonly_fields = ('created_at',)
