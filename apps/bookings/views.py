from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from apps.tours.models import Tour, TourDate
from .models import Booking

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


def booking_success_view(request, reference):
    """Displays confirmed booking voucher / ticket."""
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date', 'tour__destination'),
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
    if ref:
        searched = True
        booking = Booking.objects.filter(booking_reference=ref).first()
        
    return render(request, 'bookings/lookup.html', {
        'booking': booking,
        'searched': searched,
        'ref': ref,
    })


def download_voucher_pdf_view(request, reference):
    """Generates and serves downloadable PDF voucher for a booking."""
    from django.http import HttpResponse
    from .voucher import generate_booking_voucher_pdf

    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date', 'tour__destination'),
        booking_reference=reference
    )
    pdf_bytes = generate_booking_voucher_pdf(booking)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"BhromonGhuri_Voucher_{booking.booking_reference}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

