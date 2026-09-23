import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from apps.bookings.models import Booking
from apps.core.models import SiteSetting
from .models import Payment
from .services import PaymentGatewayService

def checkout_view(request, reference):
    """
    Renders payment checkout page with official bKash/Nagad accounts,
    mobile deep links, and manual TrxID submission.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date'), 
        booking_reference=reference
    )
    
    if booking.status == 'CONFIRMED':
        return redirect('bookings:success', reference=booking.booking_reference)
        
    if booking.status == 'PENDING_VERIFICATION':
        return redirect('payments:pending', reference=booking.booking_reference)

    site_setting = SiteSetting.load()

    return render(request, 'payments/checkout.html', {
        'booking': booking,
        'site_setting': site_setting,
    })


def submit_payment_view(request, reference):
    """
    Handles user submission of manual payment details (TrxID and sender mobile number).
    Transitions booking & payment to PENDING_VERIFICATION.
    """
    if request.method != 'POST':
        return redirect('payments:checkout', reference=reference)

    booking = get_object_or_404(Booking, booking_reference=reference)
    payment_method = request.POST.get('payment_method', 'BKASH').upper()
    sender_number = request.POST.get('sender_number', '').strip()
    transaction_id = request.POST.get('transaction_id', '').strip()

    if payment_method not in ['BKASH', 'NAGAD']:
        messages.error(request, "ব্যাংক পেমেন্ট অপশনটি আপাতত স্থগিত রয়েছে (পরবর্তীতে যুক্ত করা হবে)। অনুগ্রহ করে বিকাশ অথবা নগদ নম্বরে (01855939459) পেমেন্ট করুন।")
        return redirect('payments:checkout', reference=reference)

    if not sender_number:
        messages.error(request, "অনুগ্রহ করে আপনার প্রেরক নম্বর (Sender Mobile / Account Number) লিখুন।")
        return redirect('payments:checkout', reference=reference)

    if not transaction_id:
        messages.error(request, "অনুগ্রহ করে সঠিক ট্রানজেকশন আইডি (Transaction ID / TrxID) লিখুন।")
        return redirect('payments:checkout', reference=reference)

    payment = PaymentGatewayService.submit_manual_payment(
        booking=booking,
        method=payment_method,
        sender_number=sender_number,
        transaction_id=transaction_id
    )

    messages.success(request, "আপনার পেমেন্টের তথ্য সফলভাবে জমা দেওয়া হয়েছে! এটি এখন ম্যানুয়াল ভেরিফিকেশনে রয়েছে।")
    return redirect('payments:pending', reference=booking.booking_reference)


def pending_verification_view(request, reference):
    """
    Displays the payment pending manual verification screen.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date'),
        booking_reference=reference
    )
    latest_payment = booking.payments.order_by('-created_at').first()

    return render(request, 'payments/pending_verification.html', {
        'booking': booking,
        'payment': latest_payment,
    })


def process_simulation_view(request, reference):
    """
    Simulates immediate payment approval for automated sandbox tests.
    """
    if request.method != 'POST':
        return redirect('payments:checkout', reference=reference)

    booking = get_object_or_404(Booking, booking_reference=reference)
    payment_method = request.POST.get('payment_method', 'BKASH')
    sender_number = request.POST.get('sender_number', '01700000000')
    trx_id = request.POST.get('transaction_id', f"SIM-{booking.booking_reference}")

    payment = PaymentGatewayService.submit_manual_payment(
        booking=booking,
        method=payment_method,
        sender_number=sender_number,
        transaction_id=trx_id
    )
    PaymentGatewayService.process_confirmation(payment, success=True)
    
    messages.success(request, f"পেমেন্ট সফল ও নিশ্চিত হয়েছে! ট্রানজেকশন আইডি: {payment.transaction_id}")
    return redirect('bookings:success', reference=booking.booking_reference)


@csrf_exempt
def webhook_view(request):
    """
    Webhook listener for external payment gateways (SSLCommerz, bKash).
    """
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            trx_id = payload.get('transaction_id')
            status = payload.get('status')
            
            payment = Payment.objects.filter(transaction_id=trx_id).first()
            if payment:
                success = (status == 'VALID')
                PaymentGatewayService.process_confirmation(payment, success=success, response_data=payload)
                return JsonResponse({'status': 'ok', 'processed': True})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'ignored'}, status=200)
