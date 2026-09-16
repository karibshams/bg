from django.contrib import admin
from django.utils.html import format_html
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking_ref', 'customer', 'payment_method', 'formatted_amount', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'booking__booking_reference', 'booking__customer_name')
    readonly_fields = ('transaction_id', 'booking', 'amount', 'currency', 'created_at', 'updated_at')

    def booking_ref(self, obj):
        return obj.booking.booking_reference
    booking_ref.short_description = "Booking Reference"

    def customer(self, obj):
        return obj.booking.customer_name
    customer.short_description = "Customer"

    def formatted_amount(self, obj):
        return format_html('<span style="font-weight: bold; color: #0284c7;">৳{:,.0f}</span>', obj.amount)
    formatted_amount.short_description = "Amount"

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'SUCCESS': '#10b981',
            'FAILED': '#ef4444',
            'REFUNDED': '#6366f1',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"
