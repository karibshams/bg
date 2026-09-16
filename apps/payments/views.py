import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from apps.bookings.models import Booking
from .models import Payment
from .services import PaymentGatewayService

def checkout_view(request, reference):
    """
    Renders payment checkout page for an active booking.
    """
    booking = get_object_or_404(
        Booking.objects.select_related('tour', 'tour_date'), 
        booking_reference=reference
    )
    
    if booking.status == 'CONFIRMED':
        return redirect('bookings:success', reference=booking.booking_reference)

    return render(request, 'payments/checkout.html', {
        'booking': booking,
    })


def process_simulation_view(request, reference):
    """
    Simulates sandbox payment completion for demonstration and testing.
    """
    if request.method != 'POST':
        return redirect('payments:checkout', reference=reference)

    booking = get_object_or_404(Booking, booking_reference=reference)
    payment_method = request.POST.get('payment_method', 'BKASH')
    
    # Create and approve transaction
    payment = PaymentGatewayService.create_transaction(booking, method=payment_method)
    PaymentGatewayService.process_confirmation(
        payment, 
        success=True, 
        response_data={'simulated': True, 'account': request.POST.get('sender_account', '01700000000')}
    )
    
    messages.success(request, f"পেমেন্ট সফল হয়েছে! লেনদেন আইডি: {payment.transaction_id}")
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
