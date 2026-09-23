from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from .models import Booking
from apps.payments.models import Payment
from apps.payments.services import PaymentGatewayService

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_reference',
        'customer_name',
        'customer_phone',
        'tour_title',
        'travel_date',
        'num_travelers',
        'formatted_total',
        'payment_info',
        'status_badge',
        'approve_action',
        'voucher_link',
        'created_at'
    )
    list_filter = ('status', 'tour', 'created_at')
    search_fields = (
        'booking_reference',
        'customer_name',
        'customer_email',
        'customer_phone',
        'tour__title',
        'payments__transaction_id',
        'payments__sender_number'
    )
    readonly_fields = ('booking_reference', 'created_at', 'updated_at')
    actions = ['mark_confirmed', 'mark_rejected', 'mark_cancelled']

    def tour_title(self, obj):
        return obj.tour.bangla_title or obj.tour.title
    tour_title.short_description = "ট্যুর (Tour)"

    def travel_date(self, obj):
        if obj.tour_date:
            return obj.tour_date.start_date.strftime('%d %b %Y')
        return "Flexible"
    travel_date.short_description = "তারিখ (Date)"

    def formatted_total(self, obj):
        amount_str = f"৳{float(obj.total_amount):,.0f}" if obj.total_amount is not None else "৳0"
        return format_html('<span style="font-weight: bold; color: #0284c7;">{}</span>', amount_str)
    formatted_total.short_description = "মোট টাকা (Total)"

    def payment_info(self, obj):
        payment = obj.payments.order_by('-created_at').first()
        if payment:
            return format_html(
                '<div style="font-size: 11px; line-height: 1.3;">'
                '<strong>{}</strong><br/>'
                '<span style="font-family: monospace; color: #0284c7;">{}</span><br/>'
                '<span style="color: #64748b;">Sender: {}</span>'
                '</div>',
                payment.get_payment_method_display(),
                payment.transaction_id,
                payment.sender_number or "N/A"
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">No Trx yet</span>')
    payment_info.short_description = "পেমেন্ট তথ্য (Payment)"

    def status_badge(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'PENDING_VERIFICATION': '#f97316',
            'CONFIRMED': '#10b981',
            'CANCELLED': '#64748b',
            'REJECTED': '#ef4444',
            'COMPLETED': '#6366f1',
        }
        labels = {
            'PENDING': 'Pending Payment',
            'PENDING_VERIFICATION': 'Pending Verification (অপেক্ষমাণ)',
            'CONFIRMED': 'Confirmed (নিশ্চিত)',
            'CANCELLED': 'Cancelled',
            'REJECTED': 'Rejected (বাতিল/প্রত্যাখ্যাত)',
            'COMPLETED': 'Completed',
        }
        color = colors.get(obj.status, '#64748b')
        label = labels.get(obj.status, obj.get_status_display())
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold; display: inline-block; white-space: nowrap;">{}</span>',
            color, label
        )
    status_badge.short_description = "স্ট্যাটাস (Status)"

    def approve_action(self, obj):
        if obj.status in ['PENDING', 'PENDING_VERIFICATION']:
            approve_url = reverse('admin:booking_approve_single', args=[obj.id])
            reject_url = reverse('admin:booking_reject_single', args=[obj.id])
            return format_html(
                '<div style="display: flex; gap: 4px; align-items: center;">'
                '<a href="{}" style="background-color: #10b981; color: white; padding: 5px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; text-decoration: none; display: inline-block; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">'
                '✓ Approve'
                '</a>'
                '<a href="{}" style="background-color: #ef4444; color: white; padding: 5px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; text-decoration: none; display: inline-block; box-shadow: 0 1px 2px rgba(0,0,0,0.1);" onclick="return confirm(\'Are you sure you want to reject this booking due to invalid or unverified details?\');">'
                '✗ Reject'
                '</a>'
                '</div>',
                approve_url, reject_url
            )
        elif obj.status == 'CONFIRMED':
            return format_html('<span style="color: #10b981; font-weight: bold; font-size: 11px;">✓ অনুমোদিত (Approved)</span>')
        elif obj.status == 'REJECTED':
            return format_html('<span style="color: #ef4444; font-weight: bold; font-size: 11px;">✗ প্রত্যাখ্যাত (Rejected)</span>')
        return "-"
    approve_action.short_description = "অ্যাকশন (Action)"

    def voucher_link(self, obj):
        if obj.status == 'CONFIRMED':
            url = reverse('bookings:download_voucher', args=[obj.booking_reference])
            return format_html('<a href="{}" target="_blank" style="color: #0284c7; font-weight: bold; font-size: 11px; text-decoration: underline;">PDF Voucher ↗</a>', url)
        return "-"
    voucher_link.short_description = "ভাউচার (PDF)"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:booking_id>/approve-quick/', self.admin_site.admin_view(self.approve_single_booking), name='booking_approve_single'),
            path('<int:booking_id>/reject-quick/', self.admin_site.admin_view(self.reject_single_booking), name='booking_reject_single'),
        ]
        return custom_urls + urls

    def approve_single_booking(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        
        # Approve payment if exists
        payment = booking.payments.order_by('-created_at').first()
        if payment:
            PaymentGatewayService.process_confirmation(payment, success=True, response_data={
                'approved_by': request.user.username,
                'source': 'BookingAdmin Quick Approve'
            })
        else:
            # Fallback if no payment record was submitted
            booking.confirm_booking()
            from apps.payments.services import send_confirmation_email_with_voucher
            send_confirmation_email_with_voucher(booking)

        self.message_user(
            request,
            f"✓ বুকিং {booking.booking_reference} ({booking.customer_name}) সফলভাবে অনুমোদিত ও নিশ্চিত হয়েছে! আসন সংখ্যা আপডেট এবং ইমেইলে পিডিএফ ভাউচার পাঠানো হয়েছে।",
            level=messages.SUCCESS
        )
        return redirect('admin:bookings_booking_changelist')

    def reject_single_booking(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        reason = "অসত্য বা অমিল পেমেন্ট ট্রানজেকশন তথ্যের কারণে অ্যাডমিন কর্তৃক বুকিংটি বাতিল করা হয়েছে (Incorrect or unverified payment details)."
        payment = booking.payments.order_by('-created_at').first()
        if payment:
            PaymentGatewayService.process_confirmation(payment, success=False, response_data={
                'rejected_by': request.user.username,
                'source': 'BookingAdmin Quick Reject',
                'reason': reason
            })
        else:
            booking.reject_booking(reason=reason)

        self.message_user(
            request,
            f"✗ বুকিং {booking.booking_reference} ({booking.customer_name}) বাতিল ও প্রত্যাখ্যাত করা হয়েছে।",
            level=messages.WARNING
        )
        return redirect('admin:bookings_booking_changelist')

    @admin.action(description="✓ Approve Selected Bookings (অনুমোদন ও আসন আপডেট)")
    def mark_confirmed(self, request, queryset):
        count = 0
        for b in queryset:
            payment = b.payments.order_by('-created_at').first()
            if payment:
                PaymentGatewayService.process_confirmation(payment, success=True, response_data={
                    'approved_by': request.user.username,
                    'source': 'BookingAdmin Bulk Action'
                })
            else:
                b.confirm_booking()
                from apps.payments.services import send_confirmation_email_with_voucher
                send_confirmation_email_with_voucher(b)
            count += 1
        self.message_user(
            request,
            f"✓ {count}টি বুকিং সফলভাবে অনুমোদিত হয়েছে এবং আসন সংখ্যা আপডেট করা হয়েছে।",
            level=messages.SUCCESS
        )

    @admin.action(description="✗ Reject Selected Bookings (প্রত্যাখ্যান ও আসন ফেরত)")
    def mark_rejected(self, request, queryset):
        count = 0
        for b in queryset:
            payment = b.payments.order_by('-created_at').first()
            reason = "অসত্য বা অমিল পেমেন্ট ট্রানজেকশন তথ্যের কারণে অ্যাডমিন কর্তৃক বুকিংটি বাতিল করা হয়েছে (Incorrect or unverified payment details)."
            if payment:
                PaymentGatewayService.process_confirmation(payment, success=False, response_data={'reason': reason})
            else:
                b.reject_booking(reason=reason)
            count += 1
        self.message_user(
            request,
            f"✗ {count}টি বুকিং প্রত্যাখ্যাত করা হয়েছে।",
            level=messages.WARNING
        )

    @admin.action(description="✗ Cancel Selected Bookings (বাতিল ও আসন ফেরত)")
    def mark_cancelled(self, request, queryset):
        count = 0
        for b in queryset:
            payment = b.payments.order_by('-created_at').first()
            if payment:
                PaymentGatewayService.process_confirmation(payment, success=False)
            else:
                b.cancel_booking()
            count += 1
        self.message_user(
            request,
            f"✗ {count}টি বুকিং বাতিল করা হয়েছে।",
            level=messages.WARNING
        )
