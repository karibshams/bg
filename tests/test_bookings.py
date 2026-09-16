from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour, TourDate
from apps.bookings.models import Booking
import datetime

class BookingsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(name="Bandarban", slug="bandarban", description="Hills")
        self.tour = Tour.objects.create(
            title="Bandarban Nilgiri",
            slug="bandarban-nilgiri",
            destination=self.dest,
            price=9000.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=10),
            end_date=datetime.date.today() + datetime.timedelta(days=13),
            available_seats=10,
            is_active=True
        )

    def test_booking_model_auto_reference_and_calculation(self):
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="John Traveler",
            customer_email="john@example.com",
            customer_phone="01711111111",
            num_travelers=3,
            unit_price=9000.00,
            status='PENDING'
        )
        self.assertTrue(booking.booking_reference.startswith("BG-"))
        self.assertEqual(booking.total_amount, 27000.00)

    def test_booking_create_post(self):
        post_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'customer_name': 'Rahim Khan',
            'customer_email': 'rahim@test.com',
            'customer_phone': '01822222222',
            'num_travelers': 2,
            'special_requests': 'Vegetarian food please'
        }
        response = self.client.post(reverse('bookings:create'), post_data)
        self.assertEqual(response.status_code, 302)
        
        booking = Booking.objects.filter(customer_name='Rahim Khan').first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.total_amount, 18000.00)
        self.assertIn(booking.booking_reference, response.url)
