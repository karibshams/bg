from decimal import Decimal
import uuid
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .models import Booking
from apps.payments.models import Payment
from apps.payments.services import PaymentGatewayService
from apps.tours.models import Tour, TourDate, TourBus
from apps.bookings.views import get_or_create_default_bus, get_occupied_seats

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    change_list_template = "admin/bookings/booking/change_list.html"
    list_display = (
        'booking_reference',
        'source_badge',
        'customer_name',
        'customer_phone',
        'tour_title',
        'travel_date',
        'num_travelers',
        'formatted_total',
        'payment_info',
        'document_badge',
        'status_badge',
        'approve_action',
        'voucher_link',
        'created_at'
    )
    list_filter = ('booking_source', 'status', 'identification_type', 'tour', 'created_at')
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

    def source_badge(self, obj):
        if obj.booking_source == 'OFFLINE':
            return format_html(
                '<span style="background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; padding: 3px 8px; border-radius: 9999px; font-size: 10px; font-weight: 800; white-space: nowrap; display: inline-block; box-shadow: 0 1px 3px rgba(124, 58, 237, 0.3);">🏢 Offline Desk</span>'
            )
        return format_html(
            '<span style="background-color: #0284c7; color: white; padding: 3px 8px; border-radius: 9999px; font-size: 10px; font-weight: 800; white-space: nowrap; display: inline-block;">🌐 Online</span>'
        )
    source_badge.short_description = "উৎস (Source)"

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

    def document_badge(self, obj):
        if obj.identification_document:
            return format_html(
                '<a href="{}" target="_blank" style="padding: 4px 8px; background-color: #dcfce7; color: #166534; border: 1px solid #86efac; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 11px; display: inline-block;">✓ {}</a>',
                obj.identification_document.url,
                obj.get_identification_type_display()
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px; font-style: italic;">Pending Upload</span>')
    document_badge.short_description = "NID / Document"

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
            path('offline-create/', self.admin_site.admin_view(self.offline_booking_create_view), name='booking_offline_create'),
            path('offline-confirmation/<str:reference>/', self.admin_site.admin_view(self.offline_booking_confirmation_view), name='booking_offline_confirmation'),
            path('api/tour-details/<int:tour_id>/', self.admin_site.admin_view(self.tour_details_api), name='booking_tour_details_api'),
            path('api/tour-bus-seats/<int:tour_date_id>/', self.admin_site.admin_view(self.tour_bus_seats_api), name='booking_bus_seats_api'),
            path('<int:booking_id>/approve-quick/', self.admin_site.admin_view(self.approve_single_booking), name='booking_approve_single'),
            path('<int:booking_id>/reject-quick/', self.admin_site.admin_view(self.reject_single_booking), name='booking_reject_single'),
        ]
        return custom_urls + urls

    def offline_booking_create_view(self, request):
        """
        Custom admin view for creating manual on-spot / walk-in offline bookings
        with live bus seat selection, payment recording, and instant voucher generation.
        """
        if request.method == 'POST':
            tour_id = request.POST.get('tour_id')
            tour_date_id = request.POST.get('tour_date_id')
            num_travelers_raw = request.POST.get('num_travelers', '1')
            customer_name = request.POST.get('customer_name', '').strip()
            customer_phone = request.POST.get('customer_phone', '').strip()
            customer_email = request.POST.get('customer_email', '').strip()
            customer_address = request.POST.get('customer_address', '').strip()
            paid_amount_raw = request.POST.get('paid_amount', '').strip()
            payment_method = request.POST.get('payment_method', 'CASH')
            transaction_id = request.POST.get('transaction_id', '').strip()
            identification_type = request.POST.get('identification_type', 'NID')
            identification_number = request.POST.get('identification_number', '').strip()
            special_requests = request.POST.get('special_requests', '').strip()
            selected_seats_raw = request.POST.get('selected_seats', '').strip()
            bus_id = request.POST.get('bus_id')

            errors = []
            if not tour_id:
                errors.append("ট্যুর প্যাকেজ নির্বাচন করা আবশ্যক (Tour package is required).")
            if not customer_name:
                errors.append("গ্রাহকের নাম আবশ্যক (Customer name is required).")
            if not customer_phone:
                errors.append("গ্রাহকের ফোন নম্বর আবশ্যক (Customer phone is required).")

            try:
                num_travelers = int(num_travelers_raw)
                if num_travelers < 1:
                    errors.append("ভ্রমণকারী সংখ্যা কমপক্ষে ১ জন হতে হবে।")
            except ValueError:
                num_travelers = 1
                errors.append("ভ্রমণকারী সংখ্যা সঠিক সংখ্যায় প্রদান করুন।")

            tour = Tour.objects.filter(id=tour_id).first() if tour_id else None
            if not tour:
                errors.append("নির্বাচিত ট্যুর পাওয়া যায়নি।")

            tour_date = None
            if tour_date_id:
                tour_date = TourDate.objects.filter(id=tour_date_id, tour=tour).first()
                if not tour_date:
                    errors.append("নির্বাচিত ভ্রমণ তারিখটি পাওয়া যায়নি।")
                elif tour_date.available_seats < num_travelers:
                    errors.append(f"নির্বাচিত তারিখে পর্যাপ্ত আসন নেই (অবশিষ্ট: {tour_date.available_seats}টি, প্রয়োজন: {num_travelers}টি)।")

            # Validate seats if bus seat selection is enabled
            assigned_bus = None
            selected_seats_list = []
            if tour and tour.has_bus_seat_selection:
                if bus_id and str(bus_id).isdigit():
                    assigned_bus = tour.buses.filter(id=int(bus_id)).first()
                if not assigned_bus:
                    assigned_bus = get_or_create_default_bus(tour, tour_date)

                if selected_seats_raw:
                    selected_seats_list = [s.strip().upper() for s in selected_seats_raw.split(',') if s.strip()]
                    if len(selected_seats_list) != num_travelers:
                        errors.append(f"নির্বাচিত বাসের আসন সংখ্যা ({len(selected_seats_list)}টি) অবশ্যই ভ্রমণকারী সংখ্যার ({num_travelers} জন) সমান হতে হবে।")

                    # Check seat conflicts
                    occupied = get_occupied_seats(tour_date, assigned_bus)
                    conflict = set(selected_seats_list).intersection(occupied)
                    if conflict:
                        errors.append(f"আসন {', '.join(conflict)} ইতোমধ্যে সংরক্ষিত। অন্য আসন নির্বাচন করুন।")

            if errors:
                for err in errors:
                    messages.error(request, err)
            else:
                unit_price = getattr(tour_date, 'price', None) or (tour.price if tour else Decimal('0.00'))
                total_amount = unit_price * num_travelers
                try:
                    paid_amount = Decimal(paid_amount_raw) if paid_amount_raw else total_amount
                except Exception:
                    paid_amount = total_amount

                if not customer_email:
                    rand_suffix = uuid.uuid4().hex[:6]
                    customer_email = f"walkin-{rand_suffix}@bhromonghuri.com"

                booking = Booking(
                    tour=tour,
                    tour_date=tour_date,
                    booking_source=Booking.BOOKING_SOURCE_OFFLINE,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    num_travelers=num_travelers,
                    unit_price=unit_price,
                    total_amount=total_amount,
                    special_requests=special_requests,
                    identification_type=identification_type,
                    identification_number=identification_number,
                    selected_seats=",".join(selected_seats_list),
                    assigned_bus=assigned_bus,
                    seat_selected_at=timezone.now() if selected_seats_list else None,
                    status=Booking.STATUS_CONFIRMED,
                    created_by=request.user if request.user.is_authenticated else None,
                )
                if request.FILES.get('identification_document'):
                    booking.identification_document = request.FILES['identification_document']

                booking.save()
                booking.confirm_booking()

                trx_id = transaction_id or f"OFFLINE-REC-{booking.booking_reference}"
                Payment.objects.create(
                    booking=booking,
                    transaction_id=trx_id,
                    sender_number=customer_phone,
                    payment_method=payment_method,
                    amount=paid_amount,
                    currency='BDT',
                    status='SUCCESS',
                    verified_at=timezone.now(),
                    gateway_response=f"Admin On-Spot Booking created by: {request.user.username if request.user.is_authenticated else 'Admin'}"
                )

                messages.success(
                    request,
                    f"✓ অফলাইন বুকিং {booking.booking_reference} ({booking.customer_name}) সফলভাবে তৈরি ও নিশ্চিত হয়েছে!"
                )
                return redirect('admin:booking_offline_confirmation', reference=booking.booking_reference)

        tours = Tour.objects.filter(is_published=True).select_related('destination').prefetch_related('dates', 'buses').order_by('title')
        context = {
            **self.admin_site.each_context(request),
            'title': 'নতুন অফলাইন / অন-স্পট বুকিং এন্ট্রি (New Offline Booking)',
            'tours': tours,
            'payment_methods': Payment.METHOD_CHOICES,
        }
        return render(request, 'admin/bookings/offline_booking_create.html', context)

    def offline_booking_confirmation_view(self, request, reference):
        """
        Confirmation screen for an offline booking with immediate printable/downloadable voucher links.
        """
        booking = get_object_or_404(
            Booking.objects.select_related('tour', 'tour_date', 'assigned_bus', 'created_by').prefetch_related('payments'),
            booking_reference=reference
        )
        payment = booking.payments.filter(status='SUCCESS').first() or booking.payments.first()
        context = {
            **self.admin_site.each_context(request),
            'title': f'অফলাইন বুকিং নিশ্চিতকরণ — {booking.booking_reference}',
            'booking': booking,
            'payment': payment,
        }
        return render(request, 'admin/bookings/offline_booking_confirmation.html', context)

    def tour_details_api(self, request, tour_id):
        """Returns JSON details of a tour including dates, pricing, and bus configuration."""
        tour = get_object_or_404(Tour, id=tour_id)
        dates = [
            {
                'id': d.id,
                'start_date': d.start_date.strftime('%d %b %Y'),
                'end_date': d.end_date.strftime('%d %b %Y') if d.end_date else '',
                'available_seats': d.available_seats,
                'price': float(getattr(d, 'price', None) or tour.price),
            }
            for d in tour.dates.filter(is_active=True).order_by('start_date')
        ]
        buses = [
            {
                'id': b.id,
                'name': b.bus_name,
                'layout': b.layout_type,
                'total_seats': b.total_seats
            }
            for b in tour.buses.filter(is_active=True)
        ]
        return JsonResponse({
            'id': tour.id,
            'title': tour.title,
            'bangla_title': tour.bangla_title,
            'price': float(tour.price),
            'duration': tour.duration,
            'has_bus_seat_selection': tour.has_bus_seat_selection,
            'bus_layout_type': tour.bus_layout_type or '40',
            'dates': dates,
            'buses': buses
        })

    def tour_bus_seats_api(self, request, tour_date_id):
        """Returns JSON bus layout grid and occupied seats for a tour date."""
        tour_date = get_object_or_404(TourDate.objects.select_related('tour'), id=tour_date_id)
        tour = tour_date.tour
        if not tour.has_bus_seat_selection:
            return JsonResponse({'has_bus': False})

        bus_id = request.GET.get('bus_id')
        buses = tour.buses.filter(is_active=True)
        if not buses.exists():
            get_or_create_default_bus(tour, tour_date)
            buses = tour.buses.filter(is_active=True)

        if bus_id and str(bus_id).isdigit():
            active_bus = buses.filter(id=int(bus_id)).first() or buses.first()
        else:
            active_bus = buses.first()

        occupied = get_occupied_seats(tour_date, active_bus)
        return JsonResponse({
            'has_bus': True,
            'bus_id': active_bus.id,
            'bus_name': active_bus.bus_name,
            'layout_type': active_bus.layout_type,
            'rows': active_bus.get_seat_layout_grid(),
            'occupied_seats': list(occupied),
            'buses': [{'id': b.id, 'name': b.bus_name, 'layout': b.layout_type} for b in buses]
        })

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
