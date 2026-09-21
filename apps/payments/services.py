import uuid
import json
import logging
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from .models import Payment
from apps.bookings.voucher import generate_booking_voucher_pdf

logger = logging.getLogger(__name__)

def send_confirmation_email_with_voucher(booking):
    """
    Sends booking confirmation email to customer with generated PDF voucher attached.
    """
    if not booking or not booking.customer_email:
        return False

    subject = f"বুকিং ভাউচার ও নিশ্চিতকরণ — {booking.booking_reference} (ভ্রমণঘুড়ি)"
    body = f"""প্রিয় {booking.customer_name},

শুভেচ্ছা জানবেন! ভ্রমণঘুড়ির (BhromonGhuri) সাথে আপনার ট্যুর বুকিংটি সফলভাবে অনুমোদিত ও নিশ্চিত করা হয়েছে।

বুকিং বিবরণ:
• বুকিং রেফারেন্স: {booking.booking_reference}
• ট্যুর প্যাকেজ: {booking.tour.bangla_title or booking.tour.title}
• গন্তব্য: {booking.tour.destination.name if booking.tour.destination else 'বাংলাদেশ'}
• ভ্রমণের তারিখ: {booking.tour_date.start_date.strftime('%d %b %Y') if booking.tour_date else 'ফ্লেক্সিবল / ওপেন ব্যাচ'}
• যাত্রী সংখ্যা: {booking.num_travelers} জন
• পরিশোধিত মোট টাকা: ৳{booking.total_amount:,.0f}

আপনার অফিশিয়াল ভ্রমণ ভাউচারটি এই ইমেইলের সাথে PDF ফাইল আকারে সংযুক্ত করা হয়েছে। ভ্রমণ শুরুর দিন এটি সঙ্গে রাখুন অথবা মোবাইলে প্রদর্শন করুন।

যেকোনো জরুরি জিজ্ঞাসা ও প্রয়োজনে আমাদের হটলাইনে যোগাযোগ করুন:
+8801518919370, +8801855939459
ইমেইল: bhromonghuri@gmail.com
ওয়েবসাইট: https://bhromonghuri.com

ধন্যবাদান্তে,
ভ্রমণঘুড়ি (BhromonGhuri)
নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি
"""
    try:
        pdf_bytes = generate_booking_voucher_pdf(booking)
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.customer_email],
        )
        email.attach(
            f"BhromonGhuri_Voucher_{booking.booking_reference}.pdf",
            pdf_bytes,
            "application/pdf"
        )
        email.send(fail_silently=True)
        return True
    except Exception as e:
        logger.error(f"Error sending voucher email for booking {booking.booking_reference}: {e}")
        return False


class PaymentGatewayService:
    """
    Payment gateway service for handling manual bKash/Nagad submissions,
    admin verification, and automated confirmation workflows.
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
            sender_number=booking.customer_phone,
            amount=booking.total_amount,
            status='PENDING',
        )
        return payment

    @staticmethod
    def submit_manual_payment(booking, method='BKASH', sender_number='', transaction_id=''):
        """
        Creates or updates a manual payment submission under PENDING_VERIFICATION status.
        Does not confirm booking immediately until admin verification.
        """
        transaction_id = transaction_id.strip().upper()
        sender_number = sender_number.strip()

        # Check if payment with this transaction_id already exists
        payment, created = Payment.objects.get_or_create(
            transaction_id=transaction_id,
            defaults={
                'booking': booking,
                'payment_method': method,
                'sender_number': sender_number,
                'amount': booking.total_amount,
                'status': 'PENDING_VERIFICATION',
                'gateway_response': json.dumps({
                    'submitted_at': timezone.now().isoformat(),
                    'method': method,
                    'sender_number': sender_number,
                    'status': 'Under Manual Verification'
                })
            }
        )

        if not created:
            payment.booking = booking
            payment.payment_method = method
            payment.sender_number = sender_number
            payment.amount = booking.total_amount
            payment.status = 'PENDING_VERIFICATION'
            payment.save()

        # Set booking status to PENDING_VERIFICATION
        booking.status = 'PENDING_VERIFICATION'
        booking.save(update_fields=['status', 'updated_at'])

        return payment

    @staticmethod
    def process_confirmation(payment, success=True, response_data=None):
        """
        Confirms or rejects a payment and triggers booking status update,
        seat decrement, and automated confirmation email with PDF voucher.
        """
        booking = payment.booking

        if success:
            payment.status = 'SUCCESS'
            payment.verified_at = timezone.now()
            payment.gateway_response = json.dumps(response_data or {
                'status': 'Approved',
                'verified_at': timezone.now().isoformat()
            })
            payment.save()

            # Confirm booking and recalculate seats
            booking.confirm_booking()

            # Send confirmation email with PDF voucher
            send_confirmation_email_with_voucher(booking)
            return True
        else:
            payment.status = 'FAILED'
            payment.gateway_response = json.dumps(response_data or {
                'status': 'Declined',
                'declined_at': timezone.now().isoformat()
            })
            payment.save()

            # Cancel booking and recalculate seats
            booking.cancel_booking()
            return False
