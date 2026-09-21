from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Destination, TourCategory, Tour, TourDate, 
    TourItinerary, TourImage, TourInclusion
)

class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1
    fields = ('start_date', 'end_date', 'total_capacity', 'available_seats', 'price_override', 'is_active')


class TourItineraryInline(admin.StackedInline):
    model = TourItinerary
    extra = 1
    fields = ('day_number', 'title', 'description', 'meals', 'stay_info')


class TourInclusionInline(admin.TabularInline):
    model = TourInclusion
    extra = 2
    fields = ('item', 'is_included')


class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 3
    fields = ('image', 'caption', 'order')


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'category', 'duration', 'formatted_price', 'rating_stars', 'is_featured', 'is_published')
    list_filter = ('is_published', 'is_featured', 'destination', 'category')
    search_fields = ('title', 'bangla_title', 'description', 'destination__name')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_published')
    inlines = [TourDateInline, TourItineraryInline, TourInclusionInline, TourImageInline]

    fieldsets = (
        ('General Information', {
            'fields': ('title', 'bangla_title', 'slug', 'destination', 'category', 'badge_text')
        }),
        ('Duration & Pricing', {
            'fields': (('duration', 'duration_days'), ('price', 'discount_price'), 'max_travelers')
        }),
        ('Descriptions & Media', {
            'fields': ('short_description', 'description', 'cover_image', 'video_url')
        }),
        ('Package Inclusions & Exclusions (List Builders)', {
            'description': 'Enter items one per line to dynamically show in "What is included" and "What is excluded" on the tour page.',
            'fields': ('included_items', 'excluded_items')
        }),
        ('Reviews & Visibility', {
            'fields': (('rating', 'reviews_count'), ('is_featured', 'is_published'))
        }),
    )

    def formatted_price(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="color: #0284c7; font-weight: bold;">৳{:,.0f}</span> '
                '<span style="text-decoration: line-through; color: #94a3b8; font-size: 11px;">৳{:,.0f}</span>',
                obj.discount_price, obj.price
            )
        return format_html('<span style="color: #0284c7; font-weight: bold;">৳{:,.0f}</span>', obj.price)
    formatted_price.short_description = "Price"

    def rating_stars(self, obj):
        return format_html('<span style="color: #f59e0b;">★ {}</span>', obj.rating)
    rating_stars.short_description = "Rating"


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'bangla_name', 'tagline', 'is_featured', 'order')
    list_filter = ('is_featured',)
    search_fields = ('name', 'bangla_name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'order')


@admin.register(TourCategory)
class TourCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'bangla_name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ('tour', 'start_date', 'end_date', 'available_seats', 'price_override', 'is_active')
    list_filter = ('is_active', 'start_date', 'tour__destination')
    search_fields = ('tour__title',)
