import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tours.models import Destination, Tour, TourDate, TourBus, CorporateTour
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.core.models import SiteSetting
from apps.bookings.voucher import generate_booking_voucher_pdf
from apps.tours.corporate_voucher import generate_corporate_voucher_pdf

class Feature7AdminOfflineBookingAndWatermarkTestCase(TestCase):
    """
    Test suite for New Feature 7:
    - Admin manual / offline booking entry
    - Package, departure date, traveler count, paid amount, and bus seats selection
    - Automatic payment record creation and instant booking confirmation
    - Decrement of available seats on TourDate
    - Watermarked PDF voucher generator for offline & online clients
    - Subtle company logo watermark applied on canvas background without obstructing readability
    - Branded corporate voucher watermark
    """

    def setUp(self):
        self.client = Client()
        self.site_setting = SiteSetting.load()
        self.site_setting.save()

        # Admin user
        self.admin_user = User.objects.create_superuser(
            username='admin_feature7',
            email='admin@bhromonghuri.com',
            password='Password123!'
        )
        self.client.force_login(self.admin_user)

        # Destination & Tour
        self.dest = Destination.objects.create(
            name="Sylhet Ratargul & Bisnakandi",
            slug="sylhet-ratargul",
            description="Lush green swamp forest and crystal streams"
        )
        self.tour = Tour.objects.create(
            title="Sylhet Green Haven Expedition",
            bangla_title="সিলেট রাতারগুল ও বিছনাকান্দি অভিযান",
            slug="sylhet-green-haven",
            destination=self.dest,
            price=6500.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            duration_type='MULTI_DAY',
            has_bus_seat_selection=True,
            bus_layout_type='40',
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=14),
            end_date=datetime.date.today() + datetime.timedelta(days=17),
            total_capacity=40,
            available_seats=40,
            is_active=True
        )
        self.bus = TourBus.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            bus_name="Hino 1J AC Coach 1",
            layout_type='40',
            total_seats=40,
            is_active=True
        )

    def test_booking_model_offline_fields(self):
        """Test Booking model supports offline source and admin association."""
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            booking_source=Booking.BOOKING_SOURCE_OFFLINE,
            created_by=self.admin_user,
            customer_name="Walk-in Traveler",
            customer_phone="01711223344",
            customer_email="walkin@bhromonghuri.com",
            num_travelers=2,
            unit_price=6500.00,
            total_amount=13000.00,
            selected_seats="A1,A2",
            assigned_bus=self.bus,
            status=Booking.STATUS_CONFIRMED
        )
        self.assertTrue(booking.is_offline)
        self.assertEqual(booking.booking_source, 'OFFLINE')
        self.assertEqual(booking.created_by, self.admin_user)
        self.assertIn("BG-", booking.booking_reference)

    def test_admin_offline_booking_get_view(self):
        """Admin can load the offline booking creation interface."""
        url = reverse('admin:booking_offline_create')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "অফলাইন কাস্টমার বুকিং এন্ট্রি")
        self.assertContains(res, "Sylhet Green Haven Expedition")

    def test_admin_tour_details_api(self):
        """API returns dates, pricing, and bus configuration for dynamic admin frontend."""
        url = reverse('admin:booking_tour_details_api', args=[self.tour.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['id'], self.tour.id)
        self.assertTrue(data['has_bus_seat_selection'])
        self.assertEqual(len(data['dates']), 1)
        self.assertEqual(len(data['buses']), 1)

    def test_admin_tour_bus_seats_api(self):
        """API returns bus layout and occupied seats for a tour date."""
        # Mark A1 occupied by creating another confirmed booking
        Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Existing Passenger",
            customer_phone="01999999999",
            customer_email="p1@example.com",
            num_travelers=1,
            unit_price=6500.00,
            total_amount=6500.00,
            selected_seats="A1",
            assigned_bus=self.bus,
            status=Booking.STATUS_CONFIRMED
        )

        url = reverse('admin:booking_bus_seats_api', args=[self.tour_date.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['has_bus'])
        self.assertIn("A1", data['occupied_seats'])
        self.assertNotIn("A2", data['occupied_seats'])

    def test_admin_create_offline_booking_post_success(self):
        """Admin successfully submits an on-spot booking with bus seats and payment."""
        url = reverse('admin:booking_offline_create')
        post_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'num_travelers': 2,
            'customer_name': 'Kazi Nazrul Islam',
            'customer_phone': '01811223344',
            'customer_email': 'nazrul@example.com',
            'customer_address': 'Dhanmondi, Dhaka',
            'payment_method': 'CASH',
            'paid_amount': '13000.00',
            'transaction_id': 'CASH-OFFICE-001',
            'selected_seats': 'A3,A4',
            'bus_id': self.bus.id,
            'identification_type': 'NID',
            'identification_number': '1990123456789',
            'special_requests': 'Front row preferred for elderly traveler'
        }
        res = self.client.post(url, post_data)
        self.assertEqual(res.status_code, 302)

        booking = Booking.objects.get(customer_phone='01811223344')
        self.assertTrue(booking.is_offline)
        self.assertEqual(booking.status, Booking.STATUS_CONFIRMED)
        self.assertEqual(booking.selected_seats, 'A3,A4')
        self.assertEqual(booking.assigned_bus, self.bus)
        self.assertEqual(booking.total_amount, Decimal('13000.00'))

        # Payment record created and marked SUCCESS
        payment = booking.payments.first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'SUCCESS')
        self.assertEqual(payment.payment_method, 'CASH')
        self.assertEqual(payment.amount, Decimal('13000.00'))

        # TourDate remaining seats updated
        self.tour_date.refresh_from_db()
        self.assertEqual(self.tour_date.available_seats, 38)

        # Redirects to confirmation screen
        self.assertIn(booking.booking_reference, res.url)

    def test_admin_create_offline_booking_seat_conflict_rejection(self):
        """Offline booking fails if attempting to book already occupied seat."""
        Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Existing Passenger",
            customer_phone="01999999999",
            customer_email="p1@example.com",
            num_travelers=1,
            unit_price=6500.00,
            total_amount=6500.00,
            selected_seats="B1",
            assigned_bus=self.bus,
            status=Booking.STATUS_CONFIRMED
        )

        url = reverse('admin:booking_offline_create')
        post_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'num_travelers': 1,
            'customer_name': 'New Passenger',
            'customer_phone': '01511223344',
            'payment_method': 'CASH',
            'paid_amount': '6500.00',
            'selected_seats': 'B1',  # Already occupied!
            'bus_id': self.bus.id
        }
        res = self.client.post(url, post_data)
        self.assertEqual(res.status_code, 200)  # Form re-rendered with error
        self.assertFalse(Booking.objects.filter(customer_phone='01511223344').exists())

    def test_watermark_in_booking_voucher_pdf(self):
        """PDF voucher is generated with company logo watermark background."""
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            booking_source=Booking.BOOKING_SOURCE_OFFLINE,
            created_by=self.admin_user,
            customer_name="Mizanur Rahman",
            customer_phone="01755667788",
            customer_email="mizan@example.com",
            num_travelers=2,
            unit_price=6500.00,
            total_amount=13000.00,
            selected_seats="C1,C2",
            assigned_bus=self.bus,
            status=Booking.STATUS_CONFIRMED
        )
        Payment.objects.create(
            booking=booking,
            transaction_id="CASH-VOUCHER-01",
            sender_number="01755667788",
            payment_method="CASH",
            amount=13000.00,
            status="SUCCESS",
            verified_at=timezone.now()
        )

        pdf_bytes = generate_booking_voucher_pdf(booking)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 5000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_voucher_pdf_download_and_preview_views(self):
        """Voucher endpoint supports both attachment download and inline print preview."""
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            booking_source=Booking.BOOKING_SOURCE_OFFLINE,
            customer_name="Sufia Begum",
            customer_phone="01611223344",
            customer_email="sufia@example.com",
            num_travelers=1,
            unit_price=6500.00,
            total_amount=6500.00,
            status=Booking.STATUS_CONFIRMED
        )

        # Download attachment
        download_url = reverse('bookings:download_voucher', args=[booking.booking_reference])
        res = self.client.get(download_url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertIn('attachment', res['Content-Disposition'])

        # Print preview inline
        preview_res = self.client.get(f"{download_url}?view=inline")
        self.assertEqual(preview_res.status_code, 200)
        self.assertEqual(preview_res['Content-Type'], 'application/pdf')
        self.assertIn('inline', preview_res['Content-Disposition'])

    def test_corporate_tour_voucher_watermark(self):
        """Corporate voucher also generates cleanly with watermark background."""
        corp_tour = CorporateTour.objects.create(
            title="Grameenphone Annual Leadership Conclave",
            company_name="Grameenphone Ltd.",
            contact_person="Director of HR",
            phone="01700000000",
            email="leadership@grameenphone.com",
            start_date=datetime.date.today() + datetime.timedelta(days=30),
            end_date=datetime.date.today() + datetime.timedelta(days=33),
            num_participants=50,
            bus_count=2,
            total_cost=500000.00,
            advance_paid=250000.00,
            payment_status="PARTIAL",
            status="CONFIRMED"
        )
        pdf_bytes = generate_corporate_voucher_pdf(corp_tour)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 5000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
