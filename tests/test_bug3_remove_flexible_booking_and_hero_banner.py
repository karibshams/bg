from django.test import TestCase, Client
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.tours.models import Tour, TourCategory, Destination, TourDate

class TourDetailBatchBookingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = TourCategory.objects.create(name='Hill Trek', slug='hill-trek')
        self.destination = Destination.objects.create(
            name='Sitakunda',
            slug='sitakunda',
            description='Sitakunda hills'
        )
        
        dummy_image = SimpleUploadedFile(
            name='sitakunda_hero.jpg',
            content=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9',
            content_type='image/jpeg'
        )

        self.tour = Tour.objects.create(
            title='Amazing Sitakunda Hills & Waterfalls Tour',
            slug='amazing-sitakunda-hills-waterfalls-tour',
            category=self.category,
            destination=self.destination,
            price=Decimal('3500.00'),
            duration_days=2,
            cover_image=dummy_image
        )

        # Create active departure batch
        today = timezone.now().date()
        self.batch1 = TourDate.objects.create(
            tour=self.tour,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=7),
            total_capacity=30,
            available_seats=30,
            is_active=True
        )

    def test_sidebar_does_not_have_generic_flexible_book_now_button(self):
        """Verify the generic sidebar Book Now button is removed to eliminate unassigned bookings."""
        response = self.client.get(f'/tours/{self.tour.slug}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Must not contain generic booking link without date
        generic_link = f'/bookings/new/?tour={self.tour.slug}'
        self.assertNotIn(f'href="{generic_link}"', content)
        
        # Must contain link pointing to departure batches section
        self.assertIn('href="#departure-batches"', content)
        self.assertIn('Select Departure Batch', content)
        self.assertIn('id="departure-batches"', content)

    def test_departure_batches_have_specific_batch_booking_links(self):
        """Verify departure batches have direct booking links with exact date ID."""
        response = self.client.get(f'/tours/{self.tour.slug}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Must contain batch booking link with date parameter
        batch_link = f'/bookings/new/?tour={self.tour.slug}&amp;date={self.batch1.id}'
        batch_link_alt = f'/bookings/new/?tour={self.tour.slug}&date={self.batch1.id}'
        self.assertTrue(batch_link in content or batch_link_alt in content)
        self.assertIn('Book Seat', content)

    def test_hero_banner_renders_tour_cover_image(self):
        """Verify hero banner renders dynamic cover photo behind tour title instead of dark blue block."""
        response = self.client.get(f'/tours/{self.tour.slug}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        
        # Hero banner must render the tour's cover image url
        self.assertIn(self.tour.cover_image.url, content)
        self.assertIn('opacity-60', content)
