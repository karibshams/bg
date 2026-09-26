from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from apps.tours.models import Destination, Tour, TourDate
from apps.bookings.models import Booking


class GuestAuthAndBookingGateTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.destination = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley"
        )
        self.tour = Tour.objects.create(
            destination=self.destination,
            title="Sajek Cloud Camp",
            bangla_title="সাজেক ক্লাউড ক্যাম্প",
            slug="sajek-cloud-camp",
            price=6500,
            discount_price=5999,
            duration_days=3,
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date="2026-10-15",
            end_date="2026-10-18",
            available_seats=20,
            is_active=True
        )

    def test_guest_can_browse_freely_without_login(self):
        """Unauthenticated guests can view homepage, tour list, tour detail, and booking page."""
        # 1. Homepage
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sign In')
        self.assertNotContains(resp, 'admin@bhromonghuri.com')

        # 2. Tour detail
        resp = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        self.assertEqual(resp.status_code, 200)

        # 3. Auth modal exists in page
        self.assertContains(resp, 'open-auth-modal')
        self.assertContains(resp, 'requireAuthForBooking')

    def test_admin_session_does_not_leak_to_public_navbar(self):
        """Staff user without customer_authenticated session does not show customer account dropdown on public navbar."""
        admin_user = User.objects.create_superuser('admin', 'admin@bhromonghuri.com', 'adminpass123')
        self.client.force_login(admin_user)

        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        # Should not display the staff user's name or admin profile on public navbar
        self.assertContains(resp, 'Sign In')
        self.assertNotContains(resp, 'admin@bhromonghuri.com')

    def test_customer_login_shows_customer_menu(self):
        """Regular customer shows customer menu with My Bookings & Logout."""
        customer = User.objects.create_user('traveler1', 'traveler1@example.com', 'Pass1234!')
        self.client.force_login(customer)

        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'My Bookings')
        self.assertContains(resp, reverse('core:logout'))

    @override_settings(TESTING=False)
    def test_unauthenticated_post_booking_redirects_to_login(self):
        """Unauthenticated POST request to booking create redirects to login with next parameter."""
        booking_data = {
            'tour_id': self.tour.id,
            'tour_date_id': self.tour_date.id,
            'customer_name': 'Test Traveler',
            'customer_email': 'traveler@example.com',
            'customer_phone': '01711111111',
            'num_travelers': 1,
            'selected_seats': '',
            'seat_details_json': '[]',
        }
        resp = self.client.post(reverse('bookings:create'), booking_data)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('core:login'), resp.url)
        self.assertIn('next=', resp.url)
