import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.tours.models import Destination, TourCategory, Tour, TourDate, TourItinerary, TourInclusion
from apps.tours.widgets import QuillAdminWidget
from apps.bookings.models import Booking

User = get_user_model()

class DynamicPackageDetailsTestCase(TestCase):
    """
    Test suite verifying Problem 4 requirements:
    1. 100% Dynamic Content (guide/security info, max group size, tags, duration, overview)
    2. Multiple Departure Batches & Dynamic Real-Time Seat Tracking (total vs remaining, color statuses)
    3. Pricing & Discount Control (original budget vs discounted price)
    4. Rich Text Editor for Itinerary & Overview (Word-like WYSIWYG support with safe rendering)
    5. Dynamic Inclusions/Exclusions List Builders (clean stripping of bullet points)
    """

    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            description="Beautiful valley above clouds",
        )
        self.cat = TourCategory.objects.create(
            name="Mountains & Hills",
            bangla_name="পাহাড় ও পর্বত",
            slug="mountains-hills",
        )
        self.tour = Tour.objects.create(
            title="Sajek Cloud Adventure",
            bangla_title="সাজেক ক্লাউড অ্যাডভেঞ্চার",
            slug="sajek-cloud-adventure",
            destination=self.dest,
            category=self.cat,
            duration="3 Days / 2 Nights",
            duration_days=3,
            price=Decimal("10000.00"),
            discount_price=Decimal("8500.00"),
            max_travelers=28,
            guide_security_info="Certified Mountain Ranger & Armed Escort",
            bangla_guide_security_info="প্রশিক্ষিত মাউন্টেন রেঞ্জার ও আর্মড এসকর্ট",
            short_description="Explore Sajek with scenic views.",
            description="<p><strong>Exclusive Package</strong>: Enjoy <em>luxury cottages</em> with morning cloud view! 🌄</p>",
            included_items="• 3 Nights Luxury Eco-Cottage\n- Daily Buffet Breakfast\n* 4x4 Chander Gari transport\n✓ Professional Tour Guide",
            excluded_items="• Personal Souvenirs\n- Extra Snacks\n✕ Laundry",
            is_published=True,
        )

        today = datetime.date.today()
        # Batch 1: Available
        self.date_available = TourDate.objects.create(
            tour=self.tour,
            start_date=today + datetime.timedelta(days=7),
            end_date=today + datetime.timedelta(days=10),
            total_capacity=40,
            available_seats=28,
        )
        # Batch 2: Filling fast
        self.date_filling = TourDate.objects.create(
            tour=self.tour,
            start_date=today + datetime.timedelta(days=15),
            end_date=today + datetime.timedelta(days=18),
            total_capacity=40,
            available_seats=8,
        )
        # Batch 3: Almost full
        self.date_almost_full = TourDate.objects.create(
            tour=self.tour,
            start_date=today + datetime.timedelta(days=22),
            end_date=today + datetime.timedelta(days=25),
            total_capacity=40,
            available_seats=3,
        )
        # Batch 4: Sold out
        self.date_sold_out = TourDate.objects.create(
            tour=self.tour,
            start_date=today + datetime.timedelta(days=30),
            end_date=today + datetime.timedelta(days=33),
            total_capacity=40,
            available_seats=0,
        )

        # Itinerary with rich text formatting & emojis
        self.itinerary_1 = TourItinerary.objects.create(
            tour=self.tour,
            day_number=1,
            title="Arrival & Cloud Watching",
            description="<p>Depart from Dhaka at <strong>10:00 PM</strong> via AC Hino 1J bus 🚌.<br>Reach Khagrachhari early morning and board <span style='background-color: yellow;'>4x4 Chander Gari</span>! 🚙</p>",
            meals="Breakfast, Lunch, Dinner",
            stay_info="Sajek Eco Resort",
        )

    def test_dynamic_tour_attributes_and_admin_manageability(self):
        """Verify dynamic attributes: title, guide/security info, max travelers, duration, categories."""
        self.assertEqual(self.tour.guide_security_info, "Certified Mountain Ranger & Armed Escort")
        self.assertEqual(self.tour.max_travelers, 28)
        self.assertEqual(self.tour.category.name, "Mountains & Hills")
        self.assertEqual(self.tour.duration, "3 Days / 2 Nights")

        response = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check dynamic values rendered in HTML
        self.assertIn("Certified Mountain Ranger &amp; Armed Escort", content)
        self.assertIn("Max 28 travelers", content)
        self.assertIn("Mountains &amp; Hills", content)

    def test_pricing_and_discount_control(self):
        """Verify regular budget price and discounted price are properly computed and displayed."""
        self.assertEqual(self.tour.price, Decimal("10000.00"))
        self.assertEqual(self.tour.discount_price, Decimal("8500.00"))
        self.assertEqual(self.tour.current_price, Decimal("8500.00"))

        response = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        content = response.content.decode('utf-8')

        # Discounted current price is highlighted
        self.assertIn("8500", content)
        # Original regular price is shown with strikethrough
        self.assertIn("10000", content)

    def test_multiple_departure_batches_and_seat_statuses(self):
        """Verify multiple departure batches track total seats vs available seats with color statuses."""
        self.assertEqual(self.date_available.seat_status, 'AVAILABLE')
        self.assertEqual(self.date_filling.seat_status, 'FILLING_FAST')
        self.assertEqual(self.date_almost_full.seat_status, 'ALMOST_FULL')
        self.assertEqual(self.date_sold_out.seat_status, 'SOLD_OUT')

        response = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        content = response.content.decode('utf-8')

        # Check color-coded statuses on page
        self.assertIn("seats left", content)
        self.assertIn("Sold Out", content)
        self.assertIn("Total Capacity: 40", content)

    def test_realtime_seat_recalculation_on_booking(self):
        """Verify dynamic seat tracking updates in real-time as bookings occur."""
        initial_seats = self.date_available.available_seats
        self.assertEqual(initial_seats, 28)

        # Create a confirmed booking for 4 travelers
        booking = Booking.objects.create(
            tour=self.tour,
            tour_date=self.date_available,
            customer_name="Rahim Travel",
            customer_email="rahim@example.com",
            customer_phone="01711111111",
            num_travelers=4,
            unit_price=Decimal("8500.00"),
            total_amount=Decimal("34000.00"),
            status='CONFIRMED',
        )

        # Date capacity available seats should dynamically update to 40 - 4 = 36
        self.date_available.refresh_from_db()
        self.assertEqual(self.date_available.available_seats, 36)
        self.assertEqual(self.date_available.booked_seats, 4)

    def test_wysiwyg_itinerary_rendering_safe(self):
        """Verify WYSIWYG rich text (HTML formatting, highlights, emojis) renders without escaping."""
        response = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        content = response.content.decode('utf-8')

        # Check raw HTML tags and emojis are rendered cleanly
        self.assertIn("<strong>10:00 PM</strong>", content)
        self.assertIn("🚌", content)
        self.assertIn("🚙", content)
        self.assertIn("Arrival &amp; Cloud Watching", content)

    def test_intelligent_bullet_point_cleaner(self):
        """Verify that multiline bullet-pointed inclusions/exclusions are cleanly parsed and stripped."""
        included = self.tour.get_included_list()
        excluded = self.tour.get_excluded_list()

        # Leading bullets must be cleanly stripped
        self.assertIn("3 Nights Luxury Eco-Cottage", included)
        self.assertIn("Daily Buffet Breakfast", included)
        self.assertIn("4x4 Chander Gari transport", included)
        self.assertIn("Professional Tour Guide", included)

        self.assertIn("Personal Souvenirs", excluded)
        self.assertIn("Extra Snacks", excluded)
        self.assertIn("Laundry", excluded)

        # No bullet symbols at start
        for item in included:
            self.assertFalse(item.startswith("•"))
            self.assertFalse(item.startswith("-"))
            self.assertFalse(item.startswith("*"))
            self.assertFalse(item.startswith("✓"))

    def test_quill_admin_widget_assets(self):
        """Verify QuillAdminWidget defines media assets for offline/online rich editing."""
        widget = QuillAdminWidget()
        media = widget.media
        media_js = list(media.render_js())
        media_css = list(media.render_css())

        self.assertTrue(any("quill.min.js" in s for s in media_js))
        self.assertTrue(any("quill_admin.js" in s for s in media_js))
        self.assertTrue(any("quill.snow.css" in s for s in media_css))
        self.assertTrue(any("quill_admin.css" in s for s in media_css))
