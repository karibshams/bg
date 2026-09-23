import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from apps.tours.models import Tour, TourDate, TourBus
from .models import Booking


def get_or_create_default_bus(tour, tour_date=None):
    """Ensures at least one active TourBus exists if bus selection is enabled."""
    layout = tour.bus_layout_type or '40'
    buses = tour.buses.filter(is_active=True)
    if not buses.exists():
        bus = TourBus.objects.create(
            tour=tour,
            tour_date=tour_date,
            bus_name="Bus 1",
            bus_number="BG-Coach-01",
            layout_type=layout,
            total_seats=int(layout),
            is_active=True
        )
        return bus
    return buses.first()


def get_occupied_seats(tour_date, bus, exclude_booking=None):
    """Finds all seats currently booked or selected by other confirmed bookings on this bus."""
    if not tour_date or not bus:
        return set()
    qs = Booking.objects.filter(
        tour_date=tour_date,
        status='CONFIRMED',
        assigned_bus=bus
    )
    if exclude_booking:
        qs = qs.exclude(id=exclude_booking.id)
    
    occupied = set()
    for b in qs:
        for s in b.get_selected_seats_list():
            occupied.add(s.upper())
    return occupied


def booking_create_view(request):
    """
    Renders customer booking form with dynamic Alpine.js traveler counter
    and live subtotal calculation, then creates booking.
    """
    tour_slug = request.GET.get('tour') or request.POST.get('tour_slug')
    date_id = request.GET.get('date') or request.POST.get('tour_date')
    
    selected_tour = None
    if tour_slug:
        selected_tour = get_object_or_404(Tour, slug=tour_slug, is_published=True)
        
    selected_date = None
    if date_id and date_id.isdigit():
        selected_date = TourDate.objects.filter(id=int(date_id), is_active=True).first()

    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        tour = get_object_or_404(Tour, id=tour_id, is_published=True)
        
        selected_date_id = request.POST.get('tour_date_id')
        tour_date = None
        if selected_date_id and selected_date_id.isdigit():
            tour_date = TourDate.objects.filter(id=int(selected_date_id), tour=tour, is_active=True).first()

        name = request.POST.get('customer_name', '').strip()
        email = request.POST.get('customer_email', '').strip()
        phone = request.POST.get('customer_phone', '').strip()
        address = request.POST.get('customer_address', '').strip()
        special_requests = request.POST.get('special_requests', '').strip()
        
        try:
            num_travelers = max(1, int(request.POST.get('num_travelers', 1)))
        except ValueError:
            num_travelers = 1

        # Check seat availability if specific date chosen
        if tour_date and tour_date.available_seats < num_travelers:
            messages.error(request, f"দুঃখিত, এই তারিখে মাত্র {tour_date.available_seats}টি আসন বাকি আছে।")
            return redirect(f"/bookings/new/?tour={tour.slug}&date={tour_date.id}")

        unit_price = tour_date.effective_price if tour_date else tour.current_price
        total_amount = unit_price * num_travelers

        identification_type = request.POST.get('identification_type', 'NID')
        identification_number = request.POST.get('identification_number', '').strip()
        identification_document = request.FILES.get('identification_document')

        booking = Booking.objects.create(
            tour=tour,
            tour_date=tour_date,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            customer_address=address,
            num_travelers=num_travelers,
            unit_price=unit_price,
            total_amount=total_amount,
            special_requests=special_requests,
            identification_type=identification_type,
            identification_number=identification_number,
            identification_document=identification_document,
            status='PENDING',
        )

        # Redirect to payment checkout
        return redirect('payments:checkout', reference=booking.booking_reference)

    all_tours = Tour.objects.filter(is_published=True)
    return render(request, 'bookings/booking.html', {
        'selected_tour': selected_tour,
        'selected_date': selected_date,
        'all_tours': all_tours,
    })


def booking_upload_document_view(request, reference):
    """Allows customer to upload or update NID / Birth Certificate for their booking."""
    booking = get_object_or_404(Booking, booking_reference=reference)
    if request.method == 'POST':
        doc_file = request.FILES.get('identification_document')
        doc_type = request.POST.get('identification_type', 'NID')
        doc_num = request.POST.get('identification_number', '').strip()

        fields_to_update = ['updated_at']
        if doc_file:
            booking.identification_document = doc_file
            fields_to_update.append('identification_document')
        if doc_type:
            booking.identification_type = doc_type
            fields_to_update.append('identification_type')
        if doc_num is not None:
            booking.identification_number = doc_num
            fields_to_update.append('identification_number')

        booking.save(update_fields=fields_to_update)
        messages.success(request, "Identification document (NID / Birth Certificate) uploaded successfully! / আপনার পরিচয়পত্র সফলভাবে আপলোড হয়েছে!")
    return redirect(f"{reverse('bookings:lookup')}?ref={reference}")


def booking_success_view(request, reference):
    """Displays confirmed booking voucher / ticket."""
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date', 'tour__destination', 'assigned_bus'),
        booking_reference=reference
    )
    payment = booking.payments.filter(status='SUCCESS').first()
    return render(request, 'bookings/success.html', {
        'booking': booking,
        'payment': payment,
    })


def booking_lookup_view(request):
    """Allows customer to check booking status by reference ID."""
    booking = None
    searched = False
    ref = request.GET.get('ref', '').strip().upper()
    bus_data = None
    can_change_seats = True

    if ref:
        searched = True
        booking = Booking.objects.select_related('tour', 'tour_date', 'assigned_bus').filter(booking_reference=ref).first()
        if booking and booking.status == 'CONFIRMED' and booking.tour.has_bus_seat_selection:
            buses = booking.tour.buses.filter(is_active=True)
            if not buses.exists():
                get_or_create_default_bus(booking.tour, booking.tour_date)
                buses = booking.tour.buses.filter(is_active=True)
            active_bus = booking.assigned_bus or buses.first()
            occupied = get_occupied_seats(booking.tour_date, active_bus, exclude_booking=booking)
            
            # Check 24 hour restriction for changing seats
            if booking.selected_seats and booking.tour_date and booking.tour_date.start_date:
                from datetime import datetime, time, timedelta
                start_dt = datetime.combine(booking.tour_date.start_date, time(0, 0))
                if timezone.is_aware(timezone.now()):
                    start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
                if start_dt - timezone.now() < timedelta(hours=24):
                    can_change_seats = False

            bus_data = {
                'buses': buses,
                'active_bus': active_bus,
                'grid': active_bus.get_seat_layout_grid(),
                'occupied': list(occupied),
                'selected': booking.get_selected_seats_list(),
            }
        
    return render(request, 'bookings/lookup.html', {
        'booking': booking,
        'searched': searched,
        'ref': ref,
        'bus_data': bus_data,
        'can_change_seats': can_change_seats,
    })


def booking_select_seats_view(request, reference):
    """
    Handles user confirmation of bus seats for a CONFIRMED booking.
    Enforces traveler count matching, real-time duplicate checks, and bus assignment.
    """
    if request.method != 'POST':
        return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date'),
        booking_reference=reference
    )

    if booking.status != 'CONFIRMED':
        messages.error(request, "আসন নির্বাচন করার পূর্বে আপনার বুকিং ও পেমেন্ট ভেরিফিকেশন অনুমোদিত (Confirmed) হতে হবে।")
        return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    if not booking.tour.has_bus_seat_selection:
        messages.error(request, "এই ট্যুর প্যাকেজের জন্য বাস আসন নির্বাচন অপশনটি সক্রিয় নয়।")
        return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    # If seats already chosen, enforce 24-hour cutoff for seat changes
    if booking.selected_seats and booking.tour_date and booking.tour_date.start_date:
        from datetime import datetime, time, timedelta
        start_dt = datetime.combine(booking.tour_date.start_date, time(0, 0))
        if timezone.is_aware(timezone.now()):
            start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
        if start_dt - timezone.now() < timedelta(hours=24):
            error_msg = "ট্যুর শুরুর ২৪ ঘণ্টার মধ্যে আসন পরিবর্তন করার সুযোগ নেই।"
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_msg}, status=400)
            messages.error(request, error_msg)
            return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    seats_raw = request.POST.get('seats', '')
    bus_id = request.POST.get('bus_id')

    selected_list = []
    if seats_raw:
        selected_list = [s.strip().upper() for s in seats_raw.split(',') if s.strip()]

    if len(selected_list) != booking.num_travelers:
        error_msg = f"দয়া করে আপনার ভ্রমণকারী সংখ্যার সমান ({booking.num_travelers}টি) আসন নির্বাচন করুন।"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    buses = booking.tour.buses.filter(is_active=True)
    if not buses.exists():
        get_or_create_default_bus(booking.tour, booking.tour_date)
        buses = booking.tour.buses.filter(is_active=True)

    target_bus = None
    if bus_id and str(bus_id).isdigit():
        target_bus = buses.filter(id=int(bus_id)).first()
    if not target_bus:
        target_bus = buses.first()

    # Check for conflicts
    occupied = get_occupied_seats(booking.tour_date, target_bus, exclude_booking=booking)
    conflicts = [s for s in selected_list if s in occupied]
    if conflicts:
        error_msg = f"দুঃখিত! {', '.join(conflicts)} আসনটি ইতিমধ্যে বুক হয়ে গেছে। অনুগ্রহ করে অন্য খালি আসন বেছে নিন।"
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect(f"{reverse('bookings:lookup')}?ref={reference}")

    booking.selected_seats = ", ".join(selected_list)
    booking.assigned_bus = target_bus
    booking.seat_selected_at = timezone.now()
    booking.save(update_fields=['selected_seats', 'assigned_bus', 'seat_selected_at', 'updated_at'])

    success_msg = f"✓ আপনার বাসের আসন ({booking.selected_seats}) সফলভাবে নিশ্চিত করা হয়েছে!"
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'selected_seats': booking.selected_seats,
            'bus_name': target_bus.bus_name if target_bus else "Bus 1"
        })

    messages.success(request, success_msg)
    return redirect(f"{reverse('bookings:lookup')}?ref={reference}")


def booking_seat_map_api(request, reference):
    """Returns JSON payload of bus layout, multiple buses, and occupied seats for dynamic selection."""
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date', 'assigned_bus'),
        booking_reference=reference
    )
    if not booking.tour.has_bus_seat_selection:
        return JsonResponse({'enabled': False, 'message': 'Bus seat selection disabled for this package.'})

    bus_id = request.GET.get('bus_id')
    buses = booking.tour.buses.filter(is_active=True)
    if not buses.exists():
        get_or_create_default_bus(booking.tour, booking.tour_date)
        buses = booking.tour.buses.filter(is_active=True)

    if bus_id and str(bus_id).isdigit():
        active_bus = buses.filter(id=int(bus_id)).first() or buses.first()
    elif booking.assigned_bus:
        active_bus = booking.assigned_bus
    else:
        active_bus = buses.first()

    occupied = get_occupied_seats(booking.tour_date, active_bus, exclude_booking=booking)
    user_seats = booking.get_selected_seats_list()
    buses_data = [{'id': b.id, 'name': b.bus_name, 'layout': b.layout_type, 'total': b.total_seats} for b in buses]

    can_change_seats = True
    if booking.selected_seats and booking.tour_date and booking.tour_date.start_date:
        from datetime import datetime, time, timedelta
        start_dt = datetime.combine(booking.tour_date.start_date, time(0, 0))
        if timezone.is_aware(timezone.now()):
            start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
        if start_dt - timezone.now() < timedelta(hours=24):
            can_change_seats = False

    return JsonResponse({
        'enabled': True,
        'bus_id': active_bus.id,
        'bus_name': active_bus.bus_name,
        'layout_type': active_bus.layout_type,
        'total_seats': active_bus.total_seats,
        'rows': active_bus.get_seat_layout_grid(),
        'buses': buses_data,
        'occupied_seats': list(occupied),
        'user_seats': user_seats,
        'max_travelers': booking.num_travelers,
        'hold_seconds': 300,
        'can_change_seats': can_change_seats,
    })


def download_voucher_pdf_view(request, reference):
    """Generates and serves downloadable PDF voucher for a booking."""
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date', 'tour__destination', 'assigned_bus'),
        booking_reference=reference
    )
    from .voucher import generate_booking_voucher_pdf
    pdf_bytes = generate_booking_voucher_pdf(booking)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"BhromonGhuri_Voucher_{booking.booking_reference}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

