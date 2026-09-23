from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from .models import (
    Destination, TourCategory, Tour, TourDate, 
    TourItinerary, TourImage, TourInclusion, TourBus
)
from .widgets import QuillAdminWidget

class TourBusInline(admin.TabularInline):
    model = TourBus
    extra = 1
    fields = ('bus_name', 'bus_number', 'layout_type', 'total_seats', 'is_active')


class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1
    fields = ('start_date', 'end_date', 'total_capacity', 'available_seats', 'price_override', 'is_active')


class TourItineraryInline(admin.StackedInline):
    model = TourItinerary
    extra = 1
    fields = ('day_number', ('title', 'bangla_title'), 'description', 'bangla_description', ('meals', 'stay_info'))
    formfield_overrides = {
        models.TextField: {'widget': QuillAdminWidget(attrs={'rows': 6})},
    }


class TourInclusionInline(admin.TabularInline):
    model = TourInclusion
    extra = 2
    fields = (('item', 'bangla_item'), 'is_included')


class TourImageInline(admin.TabularInline):
    model = TourImage
    extra = 3
    fields = ('image', 'caption', 'order')


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'category', 'duration', 'formatted_price', 'bus_seat_badge', 'rating_stars', 'is_featured', 'is_published')
    list_filter = ('requires_nid_or_birth_cert', 'has_bus_seat_selection', 'bus_layout_type', 'is_published', 'is_featured', 'destination', 'category')
    search_fields = ('title', 'bangla_title', 'description', 'destination__name')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_published')
    inlines = [TourBusInline, TourDateInline, TourItineraryInline, TourInclusionInline, TourImageInline]
    formfield_overrides = {
        models.TextField: {'widget': QuillAdminWidget},
    }

    fieldsets = (
        ('General Information', {
            'fields': ('title', 'bangla_title', 'slug', 'destination', 'category', 'badge_text')
        }),
        ('Duration, Group Size, Guide & Pricing', {
            'description': 'Manage group capacity, duration, security/guide info, and dynamic regular vs discount prices.',
            'fields': (
                ('duration', 'duration_days'),
                ('price', 'discount_price'),
                'max_travelers',
                ('guide_security_info', 'bangla_guide_security_info')
            )
        }),
        ('Descriptions & Media (WYSIWYG Overview)', {
            'description': 'Provide rich text overviews, highlights, and teaser descriptions.',
            'fields': (
                'short_description', 'bangla_short_description',
                'description', 'bangla_description',
                'cover_image', 'video_url'
            )
        }),
        ('Package Inclusions & Exclusions (List Builders)', {
            'description': 'Paste or type bullet points or items one per line. Bullets, dashes, and numbers are automatically cleaned.',
            'fields': (
                'included_items', 'bangla_included_items',
                'excluded_items', 'bangla_excluded_items'
            )
        }),
        ('Bus Seat Selection Configuration', {
            'description': 'Enable/disable interactive bus seat selection and choose layouts (36, 40, or 45-seater). Multiple reserved buses can be added in the inline section below.',
            'fields': (
                ('has_bus_seat_selection', 'bus_layout_type'),
            )
        }),
        ('Identity & Verification Requirements', {
            'description': 'Configure security checkpoint and travel document requirements.',
            'fields': ('requires_nid_or_birth_cert',),
        }),
        ('Reviews & Visibility', {
            'fields': (('rating', 'reviews_count'), ('is_featured', 'is_published'))
        }),
    )

    def bus_seat_badge(self, obj):
        if obj.has_bus_seat_selection:
            return format_html(
                '<span style="background-color: #047857; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold; white-space: nowrap;">✓ {} Seats</span>',
                obj.bus_layout_type
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">Disabled</span>')
    bus_seat_badge.short_description = "Bus Seats"

    def formatted_price(self, obj):
        if obj.discount_price:
            disc = f"৳{float(obj.discount_price):,.0f}"
            orig = f"৳{float(obj.price):,.0f}"
            return format_html(
                '<span style="color: #0284c7; font-weight: bold;">{}</span> '
                '<span style="text-decoration: line-through; color: #94a3b8; font-size: 11px;">{}</span>',
                disc, orig
            )
        price_val = f"৳{float(obj.price):,.0f}" if obj.price is not None else "৳0"
        return format_html('<span style="color: #0284c7; font-weight: bold;">{}</span>', price_val)
    formatted_price.short_description = "Price"

    def rating_stars(self, obj):
        return format_html('<span style="color: #f59e0b;">★ {}</span>', obj.rating)
    rating_stars.short_description = "Rating"


@admin.register(TourBus)
class TourBusAdmin(admin.ModelAdmin):
    list_display = ('bus_name', 'tour', 'bus_number', 'layout_type', 'total_seats', 'is_active', 'created_at')
    list_filter = ('layout_type', 'is_active', 'tour')
    search_fields = ('bus_name', 'bus_number', 'tour__title')


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
    list_display = ('tour', 'start_date', 'end_date', 'total_capacity', 'available_seats', 'seat_status_pill', 'price_override', 'is_active')
    list_filter = ('is_active', 'start_date', 'tour__destination')
    search_fields = ('tour__title',)

    def seat_status_pill(self, obj):
        badge = obj.seat_status_badge
        colors = {
            'emerald': ('#059669', '#ecfdf5', '#a7f3d0'),
            'amber': ('#d97706', '#fffbeb', '#fde68a'),
            'rose': ('#dc2626', '#fef2f2', '#fecaca'),
            'slate': ('#475569', '#f8fafc', '#cbd5e1')
        }
        fg, bg, border = colors.get(badge['color'], ('#334155', '#f1f5f9', '#cbd5e1'))
        return format_html(
            '<span style="display:inline-block; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: {}; background-color: {}; border: 1px solid {};">{}</span>',
            fg, bg, border, badge['en']
        )
    seat_status_pill.short_description = "Seat Availability"


@admin.register(TourItinerary)
class TourItineraryAdmin(admin.ModelAdmin):
    list_display = ('tour', 'day_number', 'title', 'meals', 'stay_info')
    list_filter = ('tour__destination', 'tour')
    search_fields = ('title', 'bangla_title', 'description', 'tour__title')
    formfield_overrides = {
        models.TextField: {'widget': QuillAdminWidget},
    }
