from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.admin.sites import AdminSite
from apps.tours.models import Destination, TourCategory, Tour
from apps.tours.admin import TourAdmin

class TourDurationClassificationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.dest = Destination.objects.create(name="Gazipur", slug="gazipur", is_featured=True)
        self.category = TourCategory.objects.create(name="Day Outing", slug="day-outing")

        self.day_tour = Tour.objects.create(
            title="Bhawal National Park Day Outing",
            slug="bhawal-day-outing",
            destination=self.dest,
            category=self.category,
            duration="Day-Long (Single Day)",
            duration_days=1,
            duration_type="DAY_TOUR",
            price=1500,
            is_published=True
        )

        self.multi_day_tour = Tour.objects.create(
            title="Sajek Valley 3-Day Expedition",
            slug="sajek-expedition",
            destination=self.dest,
            category=self.category,
            duration="3 Days / 2 Nights",
            duration_days=3,
            duration_type="MULTI_DAY",
            price=6500,
            is_published=True
        )

    def test_duration_type_properties(self):
        self.assertTrue(self.day_tour.is_day_tour)
        self.assertEqual(self.day_tour.duration_type_badge['code'], 'DAY_TOUR')
        self.assertIn('Day Tour', self.day_tour.duration_type_badge['en'])

        self.assertFalse(self.multi_day_tour.is_day_tour)
        self.assertEqual(self.multi_day_tour.duration_type_badge['code'], 'MULTI_DAY')
        self.assertIn('Multi-Day', self.multi_day_tour.duration_type_badge['en'])

    def test_admin_duration_badge(self):
        site = AdminSite()
        admin_obj = TourAdmin(Tour, site)

        day_badge = admin_obj.duration_badge(self.day_tour)
        self.assertIn("Day Tour", day_badge)

        multi_badge = admin_obj.duration_badge(self.multi_day_tour)
        self.assertIn("Multi-Day", multi_badge)

    def test_catalog_filter_by_day_tour(self):
        response = self.client.get(reverse('tours:list'), {'duration': 'day_tour'})
        self.assertEqual(response.status_code, 200)
        tours = list(response.context['tours'])
        self.assertIn(self.day_tour, tours)
        self.assertNotIn(self.multi_day_tour, tours)

    def test_catalog_filter_by_multi_day_tour(self):
        response = self.client.get(reverse('tours:list'), {'duration': 'multi_day'})
        self.assertEqual(response.status_code, 200)
        tours = list(response.context['tours'])
        self.assertIn(self.multi_day_tour, tours)
        self.assertNotIn(self.day_tour, tours)

    def test_tour_card_and_detail_render_classification_badge(self):
        # Catalog list page
        list_resp = self.client.get(reverse('tours:list'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Day Tour")
        self.assertContains(list_resp, "Multi-Day")

        # Detail page for Day Tour
        detail_resp = self.client.get(reverse('tours:detail', args=[self.day_tour.slug]))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, "Day Tour (Single Day)")
