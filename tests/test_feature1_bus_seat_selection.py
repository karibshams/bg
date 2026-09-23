import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.tours.models import Destination, Tour, TourDate, TourBus
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.core.models import SiteSetting
from apps.bookings.voucher import generate_booking_voucher_pdf

class Feature1BusSeatSelectionTestCase(TestCase):
    """
    Test suite for New Feature 1:
    - Bus seat selection controls per tour package (enable/disable, 36/40/45 layout choices)
    - Multi-bus support (TourBus model)
    - Dynamic seat layout grid generation (36-seater, 40-seater, 45-seater)
    - Interactive seat selection API with 5-minute hold timer (300 seconds)
    - Conflict prevention: cannot book occupied seats
    - Traveler count validation: selected seats count must equal num_travelers
    - 24-hour cutoff rule: cannot change seats if tour date is within 24 hours
    - Tracking page integration: displays assigned seats and interactive seat picker
    - Printable and downloadable PDF voucher includes bus name, seats, and travel document instructions
    """

    def setUp(self):
        self.client = Client()
        self.site_setting = SiteSetting.load()
        self.site_setting.save()

        self.dest = Destination.objects.create(
            name="Sajek Valley",
            slug="sajek-valley",
            description="Kingdom of clouds"
        )
        self.tour = Tour.objects.create(
            title="Sajek Valley Luxury Cloud Adventure",
            bangla_title="সাজেক ভ্যালি লাক্সারি ক্লাউড অ্যাডভেঞ্চার",
            slug="sajek-valley-luxury",
            destination=self.dest,
            price=8500.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            has_bus_seat_selection=True,
            bus_layout_type='40',
            is_published=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=7),
            end_date=datetime.date.today() + datetime.timedelta(days=10),
            total_capacity=40,
            available_seats=40,
            is_active=True
        )
        self.bus = TourBus.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            bus_name="Scania Multi-Axle Bus 1",
            layout_type='40',
            total_seats=40
        )
        self.booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Karib Shams",
            customer_email="shams@example.com",
            customer_phone="01855939459",
            num_travelers=2,
            unit_price=8500.00,
            status='CONFIRMED',
            assigned_bus=self.bus
        )

    def test_bus_layouts_grid_generation(self):
        """Test seat layout grids for 36, 40, and 45-seater bus configurations."""
        # 36-seater (4x9)
        bus_36 = TourBus(tour=self.tour, layout_type='36')
        bus_36.save()
        self.assertEqual(bus_36.total_seats, 36)
        grid_36 = bus_36.get_seat_layout_grid()
        self.assertEqual(len(grid_36), 9)
        self.assertEqual(grid_36[0]['left'], ['A1', 'A2'])
        self.assertEqual(grid_36[0]['right'], ['A3', 'A4'])

        # 40-seater (4x10)
        bus_40 = TourBus(tour=self.tour, layout_type='40')
        bus_40.save()
        self.assertEqual(bus_40.total_seats, 40)
        grid_40 = bus_40.get_seat_layout_grid()
        self.assertEqual(len(grid_40), 10)
        self.assertEqual(grid_40[9]['row'], 'J')

        # 45-seater (5x9)
        bus_45 = TourBus(tour=self.tour, layout_type='45')
        bus_45.save()
        self.assertEqual(bus_45.total_seats, 45)
        grid_45 = bus_45.get_seat_layout_grid()
        self.assertEqual(len(grid_45), 9)
        self.assertEqual(grid_45[0]['right'], ['A3', 'A4', 'A5'])

    def test_seat_map_api(self):
        """Test seat map API returns bus layout, hold seconds (300), and available/occupied seats."""
        url = reverse('bookings:seat_map_api', kwargs={'reference': self.booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['enabled'])
        self.assertEqual(data['hold_seconds'], 300)
        self.assertEqual(data['max_travelers'], 2)
        self.assertEqual(data['bus_id'], self.bus.id)
        self.assertEqual(len(data['rows']), 10)
        self.assertIn('can_change_seats', data)
        self.assertTrue(data['can_change_seats'])

    def test_seat_selection_successful(self):
        """Test selecting bus seats successfully sets selected_seats and assigned_bus on booking."""
        url = reverse('bookings:select_seats', kwargs={'reference': self.booking.booking_reference})
        response = self.client.post(url, {
            'bus_id': self.bus.id,
            'seats': 'A1, A2'
        })
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.selected_seats, 'A1, A2')
        self.assertEqual(self.booking.assigned_bus, self.bus)
        self.assertIsNotNone(self.booking.seat_selected_at)
        self.assertEqual(self.booking.get_selected_seats_list(), ['A1', 'A2'])

    def test_seat_count_traveler_match_validation(self):
        """Test selecting mismatched number of seats returns error."""
        url = reverse('bookings:select_seats', kwargs={'reference': self.booking.booking_reference})
        # Customer booked for 2 travelers, attempts to select only 1 seat
        response = self.client.post(url, {
            'bus_id': self.bus.id,
            'seats': 'A1'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn("2টি", data['message'])

    def test_duplicate_seat_conflict_prevention(self):
        """Test real-time conflict prevention: cannot book seats already occupied by another booking."""
        # Booking 1 occupies A1, A2
        self.booking.selected_seats = "A1, A2"
        self.booking.save()

        # Another booking tries to book A2, A3
        booking_2 = Booking.objects.create(
            tour=self.tour,
            tour_date=self.tour_date,
            customer_name="Rahim Uddin",
            customer_email="rahim@example.com",
            customer_phone="01711223344",
            num_travelers=2,
            unit_price=8500.00,
            status='CONFIRMED',
            assigned_bus=self.bus
        )
        url = reverse('bookings:select_seats', kwargs={'reference': booking_2.booking_reference})
        response = self.client.post(url, {
            'bus_id': self.bus.id,
            'seats': 'A2, A3'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn("A2", data['message'])

    def test_24_hour_seat_change_cutoff(self):
        """Test that travelers cannot change seats if tour start date is within 24 hours."""
        # Set tour date to today (less than 24 hours away)
        self.tour_date.start_date = datetime.date.today()
        self.tour_date.save()

        # Assign initial seats
        self.booking.selected_seats = "A1, A2"
        self.booking.save()

        url = reverse('bookings:select_seats', kwargs={'reference': self.booking.booking_reference})
        response = self.client.post(url, {
            'bus_id': self.bus.id,
            'seats': 'B1, B2'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn("২৪ ঘণ্টার মধ্যে", data['message'])

    def test_tracking_page_renders_bus_seat_section(self):
        """Test lookup/tracking page renders bus seat reservation section and scripts."""
        url = f"{reverse('bookings:lookup')}?ref={self.booking.booking_reference}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Bus Seat Reservation", content)
        self.assertIn("busSeatPicker", content)
        self.assertIn("5-Minute Hold Timer:", content)
        self.assertIn("bus-grid-data", content)

    def test_online_voucher_and_pdf_voucher(self):
        """Test online voucher and PDF voucher include bus name, reserved seats, and mandatory travel document instruction."""
        self.booking.selected_seats = "A1, A2"
        self.booking.save()

        # Online Voucher (success.html)
        url = reverse('bookings:success', kwargs={'reference': self.booking.booking_reference})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn("Reserved Bus & Seats:", content)
        self.assertIn("A1, A2", content)
        self.assertIn("Important Tour Day Instruction:", content)
        self.assertIn("National ID card", content)

        # PDF Voucher generation
        pdf_bytes = generate_booking_voucher_pdf(self.booking)
        self.assertTrue(len(pdf_bytes) > 1000)
        # Verify PDF header magic bytes
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))
