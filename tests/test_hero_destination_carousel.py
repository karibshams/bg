from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import datetime
from apps.tours.models import Destination, Tour, TourDate


class HeroDestinationCarouselTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.destination = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            tagline="Kingdom of Clouds"
        )
        self.tour = Tour.objects.create(
            destination=self.destination,
            title="Sajek Valley: Cloud Odyssey",
            bangla_title="সাজেক ভ্যালি: মেঘের অভিযান",
            slug="sajek-valley-cloud-odyssey",
            price=6500,
            discount_price=5999,
            duration_days=3,
            is_published=True
        )
        today = timezone.now().date()
        self.upcoming_date = TourDate.objects.create(
            tour=self.tour,
            start_date=today + datetime.timedelta(days=15),
            end_date=today + datetime.timedelta(days=18),
            available_seats=18,
            is_active=True
        )

    def test_hero_carousel_context_and_rendering(self):
        """Home view context should include hero_carousel_items from upcoming tours within 60 days."""
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('hero_carousel_items', resp.context)
        items = resp.context['hero_carousel_items']
        self.assertTrue(len(items) >= 1)

        # First item should match the upcoming tour
        first = items[0]
        self.assertEqual(first['title'], self.tour.title)
        self.assertEqual(first['destination_name'], self.destination.name)
        self.assertEqual(first['price'], 5999)
        self.assertIn(self.upcoming_date.start_date.strftime('%d %b, %Y'), first['departure_date'])

        # Rendered HTML assertions
        content = resp.content.decode('utf-8')
        self.assertIn('id="hero-showcase"', content)
        self.assertIn('totalSlides:', content)
        self.assertIn('3500', content)  # Auto-rotation interval within 2-4s
        self.assertIn(self.tour.title, content)
        self.assertIn('5999', content)
        self.assertIn(self.destination.name, content)
        self.assertIn('UPCOMING TOUR', content)
        self.assertIn('Traveler Rating', content)
        self.assertIn('100% Verified & Safe', content)

    def test_hero_carousel_fallback_when_no_dates_in_60_days(self):
        """When no dates are within 60 days, hero carousel should fallback gracefully."""
        # Deactivate upcoming date
        self.upcoming_date.is_active = False
        self.upcoming_date.save()

        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('hero_carousel_items', resp.context)
        items = resp.context['hero_carousel_items']
        self.assertTrue(len(items) >= 1)
        self.assertEqual(items[0]['title'], self.tour.title)
