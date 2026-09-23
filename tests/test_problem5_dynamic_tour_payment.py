import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from apps.tours.models import Destination, Tour, TourDate
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.payments.services import PaymentGatewayService
from apps.bookings.voucher import generate_booking_voucher_pdf
from apps.core.models import SiteSetting

class Problem5DynamicTourPaymentTestCase(TestCase):
    """
    Test suite for Problem 5:
    - Dynamic tour inclusions/exclusions and batch capacity
    - Real-time seat availability and booking validation
    - Manual bKash/Nagad payment workflow (PENDING_VERIFICATION)
    - Admin approval workflow with seat recalculation
    - Automated confirmation email with PDF voucher attachment
    - PDF voucher download endpoint
    """

    def setUp(self):
        self.client = Client()
        self.site_setting = SiteSetting.load()
        self.site_setting.bkash_number = "01855939459 (Personal / Send Money)"
        self.site_setting.nagad_number = "01855939459 (Personal / Send Money)"
        self.site_setting.save()

        self.dest = Destination.objects.create(
            name="Srimangal",
            slug="srimangal",
            description="Tea capital of Bangladesh"
        )
        self.tour = Tour.objects.create(
            title="Srimangal Green Paradise",
            bangla_title="শ্রীমঙ্গল চা বাগান ও লাউয়াছড়া ভ্রমণ",
            slug="srimangal-green-paradise",
            destination=self.dest,
            price=6500.00,
            duration="2 Days / 1 Night",
            duration_days=2,
            is_published=True,
            included_items="AC Bus Transport\nResort Accommodation\nAll Meals\nForest Guide",
            excluded_items="Personal Expenses\nExtra snacks\nTips"
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=7),
            end_date=datetime.date.today() + datetime.timedelta(days=9),
            total_capacity=30,
            available_seats=30,
            is_active=True
        )

    def test_tour_inclusions_and_exclusions_list_helpers(self):
        """Test that tour models parse text list builders correctly."""
        inc_list = self.tour.get_included_list()
        self.assertEqual(len(inc_list), 4)
        self.assertIn("AC Bus Transport", inc_list)
        self.assertIn("Forest Guide", inc_list)

        exc_list = self.tour.get_excluded_list()
        self.assertEqual(len(exc_list), 3)
        self.assertIn("Personal Expenses", exc_list)

    def test_seat_capacity_and_real_time_recalculation(self):
        """Test that TourDate available seats correctly reflect confirmed bookings."""
        self.assertEqual(self.tour_date.available_seats, 30)

        # Create confirmed booking with 4 travelers
        b1 = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Traveler One",
            customer_email="traveler1@example.com",
            customer_phone="01711111111",
            num_travelers=4,
            unit_price=6500.00,
            status='CONFIRMED'
        )
        self.tour_date.update_available_seats()
        self.assertEqual(self.tour_date.available_seats, 26)

        # Create confirmed booking with 6 travelers
        b2 = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Traveler Two",
            customer_email="traveler2@example.com",
            customer_phone="01722222222",
            num_travelers=6,
            unit_price=6500.00,
            status='CONFIRMED'
        )
        self.tour_date.update_available_seats()
        self.assertEqual(self.tour_date.available_seats, 20)

        # Cancel one booking -> seats should restore
        b1.cancel_booking()
        self.assertEqual(self.tour_date.available_seats, 24)

    def test_booking_creation_seat_validation(self):
        """Test that booking rejects traveler counts exceeding available seats."""
        self.tour_date.available_seats = 2
        self.tour_date.save()

        # Attempt to book 3 travelers when only 2 seats available
        post_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'customer_name': 'Overbooked User',
            'customer_email': 'over@example.com',
            'customer_phone': '01799999999',
            'num_travelers': 3,
        }
        response = self.client.post(reverse('bookings:create'), post_data)
        # Should redirect back to form with error, no new booking created
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Booking.objects.filter(customer_name='Overbooked User').exists())

    def test_manual_payment_submission_flow(self):
        """
        Test manual payment submission flow:
        1. Booking created in PENDING
        2. User submits TrxID and sender mobile
        3. Payment and Booking transition to PENDING_VERIFICATION
        4. User redirected to pending verification screen
        """
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Kamal Hossain",
            customer_email="kamal@example.com",
            customer_phone="01811223344",
            num_travelers=2,
            unit_price=6500.00,
            status='PENDING'
        )

        # Submit manual payment
        post_data = {
            'payment_method': 'BKASH',
            'sender_number': '01811223344',
            'transaction_id': 'BKA9823KL1'
        }
        response = self.client.post(
            reverse('payments:submit', kwargs={'reference': booking.booking_reference}),
            post_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('pending', response.url)

        # Verify DB states
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'PENDING_VERIFICATION')

        payment = Payment.objects.filter(transaction_id='BKA9823KL1').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'PENDING_VERIFICATION')
        self.assertEqual(payment.sender_number, '01811223344')
        self.assertEqual(payment.amount, 13000.00)

        # Verify pending verification page loads
        pending_resp = self.client.get(reverse('payments:pending', kwargs={'reference': booking.booking_reference}))
        self.assertEqual(pending_resp.status_code, 200)
        self.assertContains(pending_resp, "BKA9823KL1")
        self.assertContains(pending_resp, "ভেরিফিকেশনের অধীনে রয়েছে")

    def test_admin_verification_approval_and_email_with_pdf(self):
        """
        Test admin approval of payment:
        1. Payment marked SUCCESS, booking marked CONFIRMED
        2. Seats decremented on TourDate
        3. Automated confirmation email sent with PDF voucher attachment
        """
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Nusrat Jahan",
            customer_email="nusrat@example.com",
            customer_phone="01988776655",
            num_travelers=3,
            unit_price=6500.00,
            status='PENDING_VERIFICATION'
        )
        payment = PaymentGatewayService.submit_manual_payment(
            booking=booking,
            method='NAGAD',
            sender_number='01988776655',
            transaction_id='NAG7766XYZ'
        )

        initial_seats = self.tour_date.available_seats  # 30

        # Process approval
        success = PaymentGatewayService.process_confirmation(payment, success=True)
        self.assertTrue(success)

        payment.refresh_from_db()
        booking.refresh_from_db()
        self.tour_date.refresh_from_db()

        self.assertEqual(payment.status, 'SUCCESS')
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertIsNotNone(payment.verified_at)
        self.assertEqual(self.tour_date.available_seats, initial_seats - 3)

        # Check automated confirmation email
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, ["nusrat@example.com"])
        self.assertIn(booking.booking_reference, sent_email.subject)
        self.assertEqual(len(sent_email.attachments), 1)
        
        filename, content, mimetype = sent_email.attachments[0]
        self.assertTrue(filename.endswith(".pdf"))
        self.assertEqual(mimetype, "application/pdf")
        self.assertGreater(len(content), 5000)

    def test_pdf_voucher_generation_and_download_view(self):
        """Test PDF voucher generation and download endpoint."""
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Tanvir Ahmed",
            customer_email="tanvir@example.com",
            customer_phone="01511223344",
            num_travelers=2,
            unit_price=6500.00,
            status='CONFIRMED'
        )
        Payment.objects.create(
            booking=booking,
            transaction_id="TRX-VOUCHER-TEST",
            payment_method="BKASH",
            sender_number="01511223344",
            amount=13000.00,
            status="SUCCESS"
        )

        # Test direct PDF generator function
        pdf_bytes = generate_booking_voucher_pdf(booking)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 10000)

        # Test download voucher view endpoint
        url = reverse('bookings:download_voucher', kwargs={'reference': booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(f'attachment; filename="BhromonGhuri_Voucher_{booking.booking_reference}.pdf"', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_problem5_official_payment_numbers_and_bank_on_hold_display(self):
        """
        Problem 5 Verification:
        1. Official number for bKash and Nagad is set to 01855939459.
        2. Checkout page explicitly displays 01855939459 for both bKash and Nagad.
        3. Bank Payment option is prominently flagged as On Hold (স্থগিত).
        """
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Payment Tester",
            customer_email="tester@example.com",
            customer_phone="01712345678",
            num_travelers=2,
            unit_price=6500.00,
            status='PENDING'
        )
        url = reverse('payments:checkout', kwargs={'reference': booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check official number 01855939459
        self.assertIn("01855939459", content)
        self.assertIn("bKash (01855939459)", content)
        self.assertIn("Nagad (01855939459)", content)

        # Check Bank Payment is marked On Hold / স্থগিত
        self.assertIn("Bank Payment", content)
        self.assertIn("On Hold", content)
        self.assertIn("Temporarily On Hold", content)

    def test_problem5_bank_payment_submission_rejected(self):
        """
        Problem 5 Verification:
        Bank payment option is suspended / on hold. Submitting with payment_method='BANK'
        must be rejected and guide the user to pay via bKash or Nagad (01855939459).
        """
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Bank Payer",
            customer_email="bankpayer@example.com",
            customer_phone="01712345678",
            num_travelers=2,
            unit_price=6500.00,
            status='PENDING'
        )
        post_data = {
            'payment_method': 'BANK',
            'sender_number': '01712345678',
            'transaction_id': 'BANK-TRX-123'
        }
        response = self.client.post(
            reverse('payments:submit', kwargs={'reference': booking.booking_reference}),
            post_data,
            follow=True
        )
        # Should redirect back to checkout with message
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("ব্যাংক পেমেন্ট অপশনটি আপাতত স্থগিত রয়েছে", content)
        self.assertIn("01855939459", content)

        # Booking should remain PENDING (not PENDING_VERIFICATION)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'PENDING')
        self.assertFalse(Payment.objects.filter(transaction_id='BANK-TRX-123').exists())

