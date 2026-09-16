from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour, TourDate
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.payments.services import PaymentGatewayService
import datetime

class PaymentsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(name="Sundarbans", slug="sundarbans", description="Forest")
        self.tour = Tour.objects.create(
            title="Sundarbans Cruise",
            slug="sundarbans-cruise",
            destination=self.dest,
            price=15000.00,
            duration="4 Days",
            duration_days=4,
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=14),
            end_date=datetime.date.today() + datetime.timedelta(days=18),
            available_seats=10,
            is_active=True
        )
        self.booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Alice Explorer",
            customer_email="alice@example.com",
            customer_phone="01933333333",
            num_travelers=2,
            unit_price=15000.00,
            status='PENDING'
        )

    def test_payment_creation_and_service_confirmation(self):
        # 1. Create transaction via service
        payment = PaymentGatewayService.create_transaction(self.booking, method='BKASH')
        self.assertEqual(payment.status, 'PENDING')
        self.assertTrue(payment.transaction_id.startswith('TRX-BKA-'))

        # 2. Confirm transaction
        success = PaymentGatewayService.process_confirmation(payment, success=True)
        self.assertTrue(success)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'SUCCESS')

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'CONFIRMED')

        # Seats should be reduced by 2 (10 - 2 = 8)
        self.tour_date.refresh_from_db()
        self.assertEqual(self.tour_date.available_seats, 8)

    def test_simulation_checkout_view_flow(self):
        post_data = {
            'payment_method': 'NAGAD',
            'sender_account': '01933333333'
        }
        response = self.client.post(
            reverse('payments:simulate', kwargs={'reference': self.booking.booking_reference}), 
            post_data
        )
        self.assertEqual(response.status_code, 302)
        
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'CONFIRMED')
        self.assertEqual(self.booking.payments.first().payment_method, 'NAGAD')
