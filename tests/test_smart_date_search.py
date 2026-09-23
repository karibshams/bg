from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, TourCategory, Tour, TourDate

class SmartDateSearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(name="Sylhet", slug="sylhet", is_featured=True)
        self.category = TourCategory.objects.create(name="Nature", slug="nature")

        self.tour1 = Tour.objects.create(
            title="Ratargul & Bisnakandi Expedition",
            slug="ratargul-bisnakandi",
            destination=self.dest,
            category=self.category,
            price=4500,
            duration="2 Days",
            is_published=True
        )
        self.tour2 = Tour.objects.create(
            title="Sreemangal Tea Garden Escape",
            slug="sreemangal-escape",
            destination=self.dest,
            category=self.category,
            price=5000,
            duration="3 Days",
            is_published=True
        )

        today = date.today()
        # Schedule Tour 1 dates
        self.t1_date_exact = TourDate.objects.create(
            tour=self.tour1,
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=12),
            total_capacity=30,
            available_seats=20,
            is_active=True
        )
        self.t1_date_plus2 = TourDate.objects.create(
            tour=self.tour1,
            start_date=today + timedelta(days=12),
            end_date=today + timedelta(days=14),
            total_capacity=30,
            available_seats=15,
            is_active=True
        )
        self.t1_date_minus3 = TourDate.objects.create(
            tour=self.tour1,
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=9),
            total_capacity=30,
            available_seats=25,
            is_active=True
        )

        # Schedule Tour 2 dates
        self.t2_date_plus1 = TourDate.objects.create(
            tour=self.tour2,
            start_date=today + timedelta(days=11),
            end_date=today + timedelta(days=14),
            total_capacity=40,
            available_seats=35,
            is_active=True
        )
        self.t2_date_plus5 = TourDate.objects.create(
            tour=self.tour2,
            start_date=today + timedelta(days=15),
            end_date=today + timedelta(days=18),
            total_capacity=40,
            available_seats=40,
            is_active=True
        )

    def test_exact_date_search_returns_matching_tour(self):
        exact_day = (date.today() + timedelta(days=10)).strftime('%Y-%m-%d')
        response = self.client.get(reverse('tours:list'), {'date': exact_day})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_exact_date_match'])
        self.assertIn(self.tour1, response.context['tours'])
        self.assertEqual(len(response.context['nearby_results']), 0)
        self.assertContains(response, "Exact Departure Date Match")

    def test_proximity_matching_when_exact_date_not_running(self):
        # Search for a date with no exact tour: today + 9 days
        searched_day = (date.today() + timedelta(days=9)).strftime('%Y-%m-%d')
        response = self.client.get(reverse('tours:list'), {'date': searched_day})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_exact_date_match'])
        
        nearby = response.context['nearby_results']
        # Must return up to 5 nearby available departure dates
        self.assertTrue(1 <= len(nearby) <= 5)

        # Check that proximity banner is rendered
        self.assertContains(response, "Alternative dates available nearby")
        self.assertContains(response, "Smart Proximity Matching")

        # The closest departure dates should be at delta = +1 day (day 10) or delta = -2 days (day 7) or delta = +2 days (day 11)
        deltas = [item['abs_delta'] for item in nearby]
        # Should be sorted in ascending order of abs_delta (closest dates first)
        self.assertEqual(deltas, sorted(deltas))
        self.assertEqual(nearby[0]['abs_delta'], 1)  # day 10 is 1 day away from day 9!

    def test_htmx_partial_returns_proximity_tour_cards(self):
        searched_day = (date.today() + timedelta(days=20)).strftime('%Y-%m-%d')
        response = self.client.get(
            reverse('tours:list'),
            {'date': searched_day},
            HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/tour_grid.html')
        self.assertContains(response, "Alternative dates available nearby")
        self.assertContains(response, "proximity-card")

    def test_detail_view_preserves_selected_date_from_search(self):
        response = self.client.get(
            reverse('tours:detail', args=[self.tour1.slug]),
            {'date': str(self.t1_date_exact.id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['selected_date_id'], self.t1_date_exact.id)
