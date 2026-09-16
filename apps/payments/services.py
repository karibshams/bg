import uuid
import json
from django.utils import timezone
from .models import Payment

class PaymentGatewayService:
    """
    Decoupled payment service for handling transactions, simulations,
    and webhook confirmations.
    """

    @staticmethod
    def create_transaction(booking, method='BKASH'):
        """Creates a pending payment record for the booking."""
        prefix = method.upper()[:3]
        trx_id = f"TRX-{prefix}-{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment.objects.create(
            booking=booking,
            transaction_id=trx_id,
            payment_method=method,
            amount=booking.total_amount,
            status='PENDING',
        )
        return payment

    @staticmethod
    def process_confirmation(payment, success=True, response_data=None):
        """
        Confirms a payment and triggers booking confirmation and seat reduction.
        """
        if success:
            payment.status = 'SUCCESS'
            payment.gateway_response = json.dumps(response_data or {'status': 'Approved', 'time': timezone.now().isoformat()})
            payment.save()

            # Confirm associated booking
            booking = payment.booking
            booking.status = 'CONFIRMED'
            booking.save()

            # Reduce seats if tied to a specific TourDate
            if booking.tour_date and booking.tour_date.available_seats >= booking.num_travelers:
                booking.tour_date.available_seats -= booking.num_travelers
                booking.tour_date.save()

            return True
        else:
            payment.status = 'FAILED'
            payment.gateway_response = json.dumps(response_data or {'status': 'Declined'})
            payment.save()
            return False
