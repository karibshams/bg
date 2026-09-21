from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Payment
from .services import PaymentGatewayService

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'booking_ref',
        'customer_name',
        'customer_phone',
        'sender_number',
        'tour_batch',
        'seats_count',
        'payment_method',
        'formatted_amount',
        'status_badge',
        'approve_action',
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = (
        'transaction_id',
        'sender_number',
        'booking__booking_reference',
        'booking__customer_name',
        'booking__customer_phone',
        'booking__tour__title'
    )
    readonly_fields = (
        'transaction_id',
        'booking',
        'sender_number',
        'payment_method',
        'amount',
        'currency',
        'gateway_response',
        'verified_at',
        'created_at',
        'updated_at'
    )
    actions = ['approve_payments', 'reject_payments']

    def booking_ref(self, obj):
        url = reverse('admin:bookings_booking_change', args=[obj.booking.id])
        return format_html('<a href="{}" style="font-weight: bold; color: #0284c7;">{}</a>', url, obj.booking.booking_reference)
    booking_ref.short_description = "Booking Ref"

    def customer_name(self, obj):
        return obj.booking.customer_name
    customer_name.short_description = "Customer"

    def customer_phone(self, obj):
        return obj.booking.customer_phone
    customer_phone.short_description = "Phone"

    def tour_batch(self, obj):
        b = obj.booking
        tour_name = b.tour.bangla_title or b.tour.title
        if b.tour_date:
            date_str = b.tour_date.start_date.strftime('%d %b')
            return f"{tour_name[:20]}... ({date_str})"
        return f"{tour_name[:20]}... (Flexible)"
    tour_batch.short_description = "Tour Batch"

    def seats_count(self, obj):
        return f"{obj.booking.num_travelers} seats"
    seats_count.short_description = "Seats"

    def formatted_amount(self, obj):
        amount_str = f"৳{float(obj.amount):,.0f}" if obj.amount is not None else "৳0"
        return format_html('<span style="font-weight: bold; color: #0284c7;">{}</span>', amount_str)
    formatted_amount.short_description = "Amount"

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PENDING_VERIFICATION': '#f97316',
            'SUCCESS': '#10b981',
            'FAILED': '#ef4444',
            'REFUNDED': '#6366f1',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold; display: inline-block; white-space: nowrap;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def approve_action(self, obj):
        if obj.status in ['PENDING', 'PENDING_VERIFICATION']:
            approve_url = reverse('admin:payment_approve_single', args=[obj.id])
            return format_html(
                '<a href="{}" style="background-color: #10b981; color: white; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; text-decoration: none; display: inline-block;">✓ Approve</a>',
                approve_url
            )
        elif obj.status == 'SUCCESS':
            voucher_url = reverse('bookings:download_voucher', args=[obj.booking.booking_reference])
            return format_html(
                '<a href="{}" target="_blank" style="color: #0284c7; font-size: 11px; font-weight: bold;">PDF Voucher ↗</a>',
                voucher_url
            )
        return "-"
    approve_action.short_description = "Action"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:payment_id>/approve-quick/', self.admin_site.admin_view(self.approve_single_payment), name='payment_approve_single'),
        ]
        return custom_urls + urls

    def approve_single_payment(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id)
        PaymentGatewayService.process_confirmation(payment, success=True, response_data={
            'approved_by': request.user.username,
            'source': 'Admin Quick Approve'
        })
        self.message_user(
            request, 
            f"পেমেন্ট {payment.transaction_id} এবং বুকিং {payment.booking.booking_reference} সফলভাবে অনুমোদিত হয়েছে। সিট সংখ্যা আপডেট ও ইমেইল ভাউচার পাঠানো হয়েছে।",
            level=messages.SUCCESS
        )
        return redirect('admin:payments_payment_changelist')

    @admin.action(description="✓ Approve Selected Payments & Confirm Bookings (অনুমোদন)")
    def approve_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            PaymentGatewayService.process_confirmation(payment, success=True, response_data={
                'approved_by': request.user.username,
                'source': 'Admin Bulk Action'
            })
            count += 1
        self.message_user(
            request,
            f"{count}টি পেমেন্ট সফলভাবে অনুমোদিত এবং সংশ্লিষ্ট বুকিং নিশ্চিত করা হয়েছে।",
            level=messages.SUCCESS
        )

    @admin.action(description="✗ Reject Selected Payments & Cancel Bookings (বাতিল)")
    def reject_payments(self, request, queryset):
        count = 0
        for payment in queryset:
            PaymentGatewayService.process_confirmation(payment, success=False, response_data={
                'rejected_by': request.user.username,
                'source': 'Admin Bulk Action'
            })
            count += 1
        self.message_user(
            request,
            f"{count}টি পেমেন্ট বাতিল করা হয়েছে।",
            level=messages.WARNING
        )
