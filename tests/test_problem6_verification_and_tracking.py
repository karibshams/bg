import datetime
from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour, TourDate
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.payments.services import PaymentGatewayService
from apps.core.models import SiteSetting

class Problem6VerificationAndTrackingTestCase(TestCase):
    """
    Test suite for Problem 6:
    - Prominent Booking Reference ID with Copy button on Payment Under Verification page
    - Mandatory notice requiring users to save their Booking Reference ID
    - Accurate payment notice warning that fake/invalid phone or TrxID leads to immediate rejection
    - Live tracking page status updates (Confirmed, Pending Verification, Rejected)
    - Specific rejection reason communicated directly via tracking notice and follow-up helpline contact
    - Admin quick reject workflow
    """

    def setUp(self):
        self.client = Client()
        self.site_setting = SiteSetting.load()
        self.site_setting.bkash_number = "01855939459 (Personal / Send Money)"
        self.site_setting.nagad_number = "01855939459 (Personal / Send Money)"
        self.site_setting.phone = "+8801518919370, +8801855939459"
        self.site_setting.save()

        self.dest = Destination.objects.create(
            name="Sajek Valley",
            slug="sajek-valley",
            description="Kingdom of clouds"
        )
        self.tour = Tour.objects.create(
            title="Sajek Valley: Kingdom of Clouds Adventure",
            bangla_title="সাজেক ভ্যালি: মেঘের রাজ্যে রোমাঞ্চকর অভিযান",
            slug="sajek-valley-adventure",
            destination=self.dest,
            price=8500.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=10),
            end_date=datetime.date.today() + datetime.timedelta(days=13),
            total_capacity=30,
            available_seats=30,
            is_active=True
        )
        self.booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Karib Shams",
            customer_email="shams22karib@gmail.com",
            customer_phone="01683168977",
            num_travelers=4,
            unit_price=8500.00,
            status='PENDING_VERIFICATION'
        )
        self.payment = Payment.objects.create(
            booking=self.booking,
            transaction_id="3425436546",
            payment_method="BKASH",
            sender_number="01683168977",
            amount=34000.00,
            status="PENDING_VERIFICATION"
        )

    def test_pending_verification_has_copy_button_and_mandatory_notice(self):
        """
        Verify Payment Under Verification page:
        1. Reference ID is rendered with a dedicated Copy button.
        2. Prominent mandatory notice instructing user to save Reference ID.
        """
        url = reverse('payments:pending', kwargs={'reference': self.booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check Reference ID & Copy button
        self.assertIn(self.booking.booking_reference, content)
        self.assertIn("copyRef()", content)
        self.assertIn("Copy", content)

        # Check Mandatory Notice
        self.assertIn("Mandatory Notice: Please Save Your Booking Reference ID!", content)
        self.assertIn("Track Booking", content)

    def test_pending_verification_has_accurate_payment_notice(self):
        """
        Verify Payment Under Verification page has accurate payment notice:
        Sender mobile banking number and TrxID must be 100% valid; fake details result in immediate rejection.
        """
        url = reverse('payments:pending', kwargs={'reference': self.booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn("Accurate Payment Notice — Strict Verification Policy", content)
        self.assertIn("100% valid", content)
        self.assertIn("immediate rejection", content)

    def test_tracking_lookup_page_mandatory_notice_and_copy(self):
        """
        Verify lookup (Track Booking) page displays mandatory notice and search capabilities.
        """
        url = reverse('bookings:lookup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn("Mandatory Notice: Save Your Booking Reference ID", content)
        self.assertIn("BG-2026-", content)

    def test_tracking_lookup_pending_and_confirmed_flow(self):
        """
        Verify tracking lookup displays pending and confirmed states.
        """
        lookup_url = reverse('bookings:lookup') + f"?ref={self.booking.booking_reference}"
        response = self.client.get(lookup_url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Currently PENDING_VERIFICATION
        self.assertIn("Pending Verification", content)
        self.assertIn("Payment Under Verification", content)

        # Approve booking
        PaymentGatewayService.process_confirmation(self.payment, success=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'CONFIRMED')

        # Now lookup should show Confirmed with voucher links
        response_confirmed = self.client.get(lookup_url)
        self.assertEqual(response_confirmed.status_code, 200)
        content_confirmed = response_confirmed.content.decode('utf-8')
        self.assertIn("Payment Verified & Booking Confirmed!", content_confirmed)
        self.assertIn("Voucher PDF", content_confirmed)
        self.assertIn("Online Voucher", content_confirmed)

    def test_tracking_and_verification_rejection_updates_with_specific_reason(self):
        """
        Verify that if a booking is rejected:
        1. Specific rejection reason is saved on Booking model.
        2. Tracking lookup page displays 'Rejected', specific reason, and helpline contact info.
        3. Pending verification page displays 'Booking Rejected' with reason and helpline contact info.
        """
        specific_reason = "Transaction ID 3425436546 does not match bKash statement records (Fake TrxID)."
        PaymentGatewayService.process_confirmation(self.payment, success=False, response_data={
            'rejection_reason': specific_reason
        })

        self.booking.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(self.booking.status, 'REJECTED')
        self.assertEqual(self.payment.status, 'FAILED')
        self.assertEqual(self.booking.rejection_reason, specific_reason)

        # 1. Check Tracking page
        lookup_url = reverse('bookings:lookup') + f"?ref={self.booking.booking_reference}"
        lookup_resp = self.client.get(lookup_url)
        self.assertEqual(lookup_resp.status_code, 200)
        lookup_content = lookup_resp.content.decode('utf-8')
        self.assertIn("Booking Rejected", lookup_content)
        self.assertIn(specific_reason, lookup_content)
        self.assertIn("+8801855939459", lookup_content)

        # 2. Check Pending/Verification page
        pending_url = reverse('payments:pending', kwargs={'reference': self.booking.booking_reference})
        pending_resp = self.client.get(pending_url)
        self.assertEqual(pending_resp.status_code, 200)
        pending_content = pending_resp.content.decode('utf-8')
        self.assertIn("Booking Rejected", pending_content)
        self.assertIn(specific_reason, pending_content)
        self.assertIn("+8801855939459", pending_content)
