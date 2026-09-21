from django.contrib import admin
from django.utils.html import format_html
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer_name', 'tour_title', 'travel_date', 'num_travelers', 'formatted_total', 'status_badge', 'voucher_link', 'created_at')
    list_filter = ('status', 'created_at', 'tour')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'customer_phone', 'tour__title')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_cancelled']

    def tour_title(self, obj):
        return obj.tour.title
    tour_title.short_description = "Tour"

    def travel_date(self, obj):
        if obj.tour_date:
            return obj.tour_date.start_date.strftime('%d %b %Y')
        return "Flexible"
    travel_date.short_description = "Travel Date"

    def formatted_total(self, obj):
        return format_html('<span style="font-weight: bold; color: #0284c7;">৳{:,.0f}</span>', obj.total_amount)
    formatted_total.short_description = "Total Amount"

    def voucher_link(self, obj):
        from django.urls import reverse
        if obj.status == 'CONFIRMED':
            url = reverse('bookings:download_voucher', args=[obj.booking_reference])
            return format_html('<a href="{}" target="_blank" style="color: #0284c7; font-weight: bold;">PDF Voucher ↗</a>', url)
        return "-"
    voucher_link.short_description = "Voucher"

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PENDING_VERIFICATION': '#f97316',
            'CONFIRMED': '#10b981',
            'CANCELLED': '#ef4444',
            'COMPLETED': '#6366f1',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    @admin.action(description="✓ Mark selected bookings as Confirmed (Update Seats)")
    def mark_confirmed(self, request, queryset):
        for b in queryset:
            b.confirm_booking()

    @admin.action(description="✗ Mark selected bookings as Cancelled (Restore Seats)")
    def mark_cancelled(self, request, queryset):
        for b in queryset:
            b.cancel_booking()
