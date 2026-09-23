import os
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from apps.tours.models import Destination, TourCategory, Tour, TourDate
from apps.bookings.models import Booking
from apps.bookings.admin import BookingAdmin
from apps.bookings.voucher import generate_booking_voucher_pdf
from django.contrib.admin.sites import AdminSite

MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NIDUploadTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(name="Bandarban", is_featured=True)
        self.category = TourCategory.objects.create(name="Adventure", slug="adventure")
        self.tour = Tour.objects.create(
            title="Bandarban Expedition",
            destination=self.dest,
            category=self.category,
            price=6500,
            duration="3 Days",
            requires_nid_or_birth_cert=True,
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=timezone.now().date() + timezone.timedelta(days=10),
            end_date=timezone.now().date() + timezone.timedelta(days=13),
            total_capacity=30,
            available_seats=30
        )

    def test_booking_creation_with_nid_upload(self):
        dummy_file = SimpleUploadedFile(
            "test_nid.jpg",
            b"fake_image_content_for_nid",
            content_type="image/jpeg"
        )
        post_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'customer_name': 'Sakib Al Hasan',
            'customer_email': 'sakib@example.com',
            'customer_phone': '01811223344',
            'num_travelers': 2,
            'customer_address': 'Dhaka, Bangladesh',
            'special_requests': 'Window seats preferred',
            'identification_type': 'NID',
            'identification_number': '19901234567890',
            'identification_document': dummy_file
        }
        response = self.client.post(reverse('bookings:create'), data=post_data)
        self.assertEqual(response.status_code, 302)

        booking = Booking.objects.get(customer_email='sakib@example.com')
        self.assertEqual(booking.identification_type, 'NID')
        self.assertEqual(booking.identification_number, '19901234567890')
        self.assertTrue(bool(booking.identification_document))
        self.assertTrue(booking.identification_document.name.startswith('bookings/documents/'))

    def test_retroactive_nid_upload_from_tracker(self):
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name='Rahim Uddin',
            customer_email='rahim@example.com',
            customer_phone='01711223344',
            num_travelers=1,
            unit_price=6500,
            total_amount=6500,
            status='PENDING'
        )
        self.assertFalse(bool(booking.identification_document))

        # Upload document via tracker upload route
        dummy_pdf = SimpleUploadedFile(
            "birth_certificate.pdf",
            b"%PDF-1.4 fake_pdf_data",
            content_type="application/pdf"
        )
        upload_url = reverse('bookings:upload_document', args=[booking.booking_reference])
        response = self.client.post(upload_url, data={
            'identification_type': 'BIRTH_CERT',
            'identification_number': '20051234567890123',
            'identification_document': dummy_pdf
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(f"ref={booking.booking_reference}", response.url)

        booking.refresh_from_db()
        self.assertEqual(booking.identification_type, 'BIRTH_CERT')
        self.assertEqual(booking.identification_number, '20051234567890123')
        self.assertTrue(bool(booking.identification_document))

    def test_admin_badge_display(self):
        site = AdminSite()
        admin_obj = BookingAdmin(Booking, site)

        booking_without_doc = Booking.objects.create(
            tour=self.tour,
            customer_name='Karim Mia',
            customer_email='karim@example.com',
            customer_phone='01611223344',
            num_travelers=1,
            unit_price=6500,
            total_amount=6500
        )
        badge_html = admin_obj.document_badge(booking_without_doc)
        self.assertIn("Pending Upload", badge_html)

        dummy_file = SimpleUploadedFile("nid.png", b"png_data", content_type="image/png")
        booking_without_doc.identification_document = dummy_file
        booking_without_doc.identification_type = 'NID'
        booking_without_doc.save()

        badge_html_with_doc = admin_obj.document_badge(booking_without_doc)
        self.assertIn("National ID Card", badge_html_with_doc)
        self.assertIn(booking_without_doc.identification_document.url, badge_html_with_doc)

    def test_voucher_generation_with_id_details(self):
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name='Hasan Mahmud',
            customer_email='hasan@example.com',
            customer_phone='01511223344',
            num_travelers=2,
            unit_price=6500,
            total_amount=13000,
            identification_type='NID',
            identification_number='198899887766',
            status='CONFIRMED'
        )
        pdf_bytes = generate_booking_voucher_pdf(booking)
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_lookup_and_success_pages_render_id_section(self):
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name='Jamal Hossain',
            customer_email='jamal@example.com',
            customer_phone='01911223344',
            num_travelers=1,
            unit_price=6500,
            total_amount=6500,
            status='CONFIRMED'
        )
        # Test tracker lookup page
        lookup_resp = self.client.get(f"{reverse('bookings:lookup')}?ref={booking.booking_reference}")
        self.assertEqual(lookup_resp.status_code, 200)
        self.assertContains(lookup_resp, "identification_document")
        self.assertContains(lookup_resp, "NID / Birth Certificate Verification")

        # Test success voucher page
        success_resp = self.client.get(reverse('bookings:success', args=[booking.booking_reference]))
        self.assertEqual(success_resp.status_code, 200)
        self.assertContains(success_resp, "Identification Document")
