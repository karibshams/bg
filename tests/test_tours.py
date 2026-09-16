from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, TourCategory, Tour, TourDate
import datetime

class ToursTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.destination = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            description="Cloud kingdom of Bangladesh"
        )
        self.category = TourCategory.objects.create(
            name="Mountain",
            slug="mountain"
        )
        self.tour = Tour.objects.create(
            title="Sajek Cloud Adventure",
            slug="sajek-cloud-adventure",
            destination=self.destination,
            category=self.category,
            price=8500.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            is_published=True,
            is_featured=True
        )
        self.tour_date = TourDate.objects.create(
            tour=self.tour,
            start_date=datetime.date.today() + datetime.timedelta(days=5),
            end_date=datetime.date.today() + datetime.timedelta(days=8),
            available_seats=15,
            is_active=True
        )

    def test_tour_creation_and_properties(self):
        self.assertEqual(self.tour.current_price, 8500.00)
        self.assertEqual(self.tour.dates.count(), 1)
        self.assertEqual(str(self.destination), "Sajek Valley (সাজেক ভ্যালি)")

    def test_tour_list_view_full_page(self):
        response = self.client.get(reverse('tours:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sajek Cloud Adventure")
        self.assertTemplateUsed(response, 'tours/list.html')

    def test_tour_list_view_htmx_partial(self):
        # When HX-Request header is sent, it should return only the partial
        response = self.client.get(reverse('tours:list'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/tour_grid.html')
        self.assertTemplateNotUsed(response, 'tours/list.html')

    def test_tour_detail_view(self):
        response = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tour.title)
        self.assertTemplateUsed(response, 'tours/detail.html')
