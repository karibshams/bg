from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.http import HttpResponse
from django.urls import path, reverse
from django.shortcuts import get_object_or_404
from .models import (
    Destination, TourCategory, Tour, TourDate, 
    TourItinerary, TourImage, TourInclusion, TourBus,
    CorporateTour, CorporateItinerary
)
from .corporate_voucher import generate_corporate_voucher_pdf
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
    list_display = ('title', 'destination', 'category', 'duration_badge', 'duration', 'formatted_price', 'bus_seat_badge', 'rating_stars', 'is_featured', 'is_published')
    list_filter = ('duration_type', 'requires_nid_or_birth_cert', 'has_bus_seat_selection', 'bus_layout_type', 'is_published', 'is_featured', 'destination', 'category')
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
            'description': 'Manage tour classification (Day-Long vs Multi-Day), duration, capacity, and pricing.',
            'fields': (
                ('duration_type', 'duration_days'),
                'duration',
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

    def duration_badge(self, obj):
        badge = obj.duration_type_badge
        if badge['code'] == 'DAY_TOUR':
            return format_html(
                '<span style="background-color: #fef3c7; color: #92400e; border: 1px solid #fde68a; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold; white-space: nowrap;">☀️ Day Tour</span>'
            )
        return format_html(
            '<span style="background-color: #e0f2fe; color: #075985; border: 1px solid #bae6fd; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold; white-space: nowrap;">🗓️ Multi-Day</span>'
        )
    duration_badge.short_description = "Duration Type"

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
    list_display = ('name', 'bangla_name', 'tagline', 'coordinates_display', 'is_featured', 'order')
    list_filter = ('is_featured',)
    search_fields = ('name', 'bangla_name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'order')

    def coordinates_display(self, obj):
        lat, lng = obj.get_coordinates()
        coords_str = f"📍 {lat:.4f}, {lng:.4f}"
        return format_html('<span style="font-family: monospace; font-size: 11px; color: #0284c7;">{}</span>', coords_str)
    coordinates_display.short_description = "Map Coordinates"


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


class CorporateItineraryInline(admin.StackedInline):
    model = CorporateItinerary
    extra = 1
    fields = ('day_number', 'title', 'description', 'stay_info')


@admin.register(CorporateTour)
class CorporateTourAdmin(admin.ModelAdmin):
    list_display = (
        'reference_code',
        'company_name',
        'title',
        'destinations_display',
        'travel_schedule',
        'num_participants',
        'bus_summary',
        'formatted_total',
        'payment_badge',
        'status_badge',
        'voucher_action',
        'created_at'
    )
    list_filter = ('status', 'payment_status', 'destinations', 'start_date', 'created_at')
    search_fields = (
        'reference_code',
        'company_name',
        'contact_person',
        'phone',
        'email',
        'title',
        'route_summary'
    )
    filter_horizontal = ('destinations',)
    inlines = [CorporateItineraryInline]
    readonly_fields = ('reference_code', 'due_amount_display', 'created_at', 'updated_at')

    fieldsets = (
        ('Client Organization & Contact Person', {
            'description': 'Details of the corporate client and primary focal person.',
            'fields': (
                ('company_name', 'reference_code'),
                ('contact_person', 'designation'),
                ('phone', 'email'),
                'office_address'
            )
        }),
        ('Event Scope & Multi-Destination Configuration', {
            'description': 'Specify multiple destinations and custom travel route.',
            'fields': (
                ('title', 'bangla_title'),
                'destinations',
                'route_summary',
                ('start_date', 'end_date', 'duration_text'),
                'num_participants'
            )
        }),
        ('Logistics, Buses & Hospitality Breakdown', {
            'description': 'Manage bus arrangements, resort accommodations, and food/catering.',
            'fields': (
                ('bus_count', 'bus_type'),
                'accommodation_details',
                'catering_details'
            )
        }),
        ('Cost Breakdown & Payment Billing', {
            'description': 'Package contract price, advance payments received, and due balance.',
            'fields': (
                ('total_cost', 'advance_paid', 'due_amount_display'),
                'payment_status'
            )
        }),
        ('Administrative Reminders & Special Requirements', {
            'description': 'Operational notes, conference/AV setups, driver and escort reminders.',
            'fields': (
                'special_requirements',
                'reminder_notes'
            )
        }),
        ('Event Lifecycle Status', {
            'fields': (
                'status',
                ('created_at', 'updated_at')
            )
        })
    )

    def destinations_display(self, obj):
        return obj.get_destinations_display()
    destinations_display.short_description = "Destinations (গন্তব্যসমূহ)"

    def travel_schedule(self, obj):
        return f"{obj.start_date.strftime('%d %b %Y')} ({obj.duration_text})"
    travel_schedule.short_description = "Schedule / Duration"

    def bus_summary(self, obj):
        return f"{obj.bus_count} Bus(es)"
    bus_summary.short_description = "Transport"

    def formatted_total(self, obj):
        return format_html('<span style="font-weight: bold; color: #0284c7;">৳{:,.0f}</span>', obj.total_cost)
    formatted_total.short_description = "Budget (BDT)"

    def due_amount_display(self, obj):
        due = obj.due_amount
        color = '#b91c1c' if due > 0 else '#047857'
        return format_html('<span style="font-weight: bold; color: {};">৳{:,.2f}</span>', color, due)
    due_amount_display.short_description = "Balance Due (BDT)"

    def payment_badge(self, obj):
        colors = {
            'PENDING': ('#b91c1c', '#fef2f2', '#fecaca'),
            'PARTIAL': ('#d97706', '#fffbeb', '#fde68a'),
            'PAID': ('#059669', '#ecfdf5', '#a7f3d0'),
        }
        fg, bg, border = colors.get(obj.payment_status, ('#334155', '#f1f5f9', '#cbd5e1'))
        return format_html(
            '<span style="padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: {}; background-color: {}; border: 1px solid {};">{}</span>',
            fg, bg, border, obj.get_payment_status_display()
        )
    payment_badge.short_description = "Payment Status"

    def status_badge(self, obj):
        colors = {
            'PROPOSAL': '#f59e0b',
            'CONFIRMED': '#10b981',
            'IN_PROGRESS': '#0284c7',
            'COMPLETED': '#6366f1',
            'CANCELLED': '#64748b',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Event Status"

    def voucher_action(self, obj):
        url = reverse('admin:corporate_tour_voucher', args=[obj.id])
        return format_html(
            '<a href="{}" target="_blank" style="padding: 4px 8px; background-color: #0284c7; color: white; border-radius: 6px; font-size: 11px; font-weight: bold; text-decoration: none; display: inline-block;">PDF Voucher ↗</a>',
            url
        )
    voucher_action.short_description = "Corporate Voucher"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/voucher/', self.admin_site.admin_view(self.download_voucher_view), name='corporate_tour_voucher'),
        ]
        return custom_urls + urls

    def download_voucher_view(self, request, object_id):
        corporate_tour = get_object_or_404(CorporateTour, id=object_id)
        pdf_bytes = generate_corporate_voucher_pdf(corporate_tour)
        filename = f"BhromonGhuri_Corporate_Voucher_{corporate_tour.reference_code}.pdf"
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        return response

