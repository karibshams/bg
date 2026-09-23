import json
from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour, TourCategory
from apps.core.models import SiteSetting
from apps.tours.admin import DestinationAdmin
from django.contrib.admin.sites import AdminSite

class Feature8InteractiveBangladeshMapTestCase(TestCase):
    """
    Test suite for New Feature 8: Interactive Bangladesh Travel Map
    - Map access button ("Explore Bangladesh Map" / "Visit Bangladesh Map") across website
    - Free & open-source map integration with Leaflet.js & OpenStreetMap (zero paid APIs)
    - Destination markers & pins with exact geographical coordinates (Sajek, Cox's Bazar, etc.)
    - Location guide & tour package previews on pin click
    - API endpoint serving destinations and tour packages data
    """

    def setUp(self):
        self.client = Client()
        self.site_setting = SiteSetting.load()
        self.site_setting.save()

        self.category = TourCategory.objects.create(
            name="Hill Tracts Adventure",
            bangla_name="পাহাড়ি রোমাঞ্চ",
            slug="hill-tracts"
        )

        self.dest_sajek = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            tagline="Kingdom of Clouds and Green Hills",
            description="A serene valley situated in Baghaichhari Upazila of Rangamati district."
        )

        self.dest_cox = Destination.objects.create(
            name="Cox's Bazar",
            bangla_name="কক্সবাজার",
            slug="coxs-bazar",
            tagline="World's Longest Natural Sea Beach",
            description="A mesmerizing 120 km unbroken sandy sea beach."
        )

        self.tour_sajek = Tour.objects.create(
            title="Sajek Cloud Camp & Valley Escape",
            bangla_title="সাজেক ক্লাউড ক্যাম্প ও ভ্যালি এস্কেপ",
            slug="sajek-cloud-camp",
            destination=self.dest_sajek,
            category=self.category,
            price=7500.00,
            duration="3 Days / 2 Nights",
            duration_days=3,
            duration_type="MULTI_DAY",
            is_published=True
        )

    def test_destination_model_coordinates(self):
        """Destination automatically assigns and resolves accurate Bangladesh coordinates."""
        coords_sajek = self.dest_sajek.get_coordinates()
        self.assertAlmostEqual(coords_sajek[0], 23.3820, places=3)
        self.assertAlmostEqual(coords_sajek[1], 92.2938, places=3)

        coords_cox = self.dest_cox.get_coordinates()
        self.assertAlmostEqual(coords_cox[0], 21.4272, places=3)
        self.assertAlmostEqual(coords_cox[1], 91.9701, places=3)

        # Custom coordinates support
        custom_dest = Destination.objects.create(
            name="Jaflong Stone River",
            slug="jaflong",
            latitude=25.1634,
            longitude=92.0199
        )
        self.assertEqual(custom_dest.get_coordinates(), (25.1634, 92.0199))

    def test_destination_admin_coordinates_display(self):
        """Admin panel displays formatted map coordinates."""
        admin_obj = DestinationAdmin(Destination, AdminSite())
        display_html = admin_obj.coordinates_display(self.dest_sajek)
        self.assertIn("📍", display_html)
        self.assertIn("23.3820", display_html)
        self.assertIn("92.2938", display_html)

    def test_interactive_map_view(self):
        """Interactive map page loads successfully with Leaflet and OSM assets."""
        url = reverse('tours:interactive_map')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # Check Leaflet & CartoDB Voyager integration (Zero 403 tile blocking, zero API costs)
        self.assertContains(res, "leaflet.js")
        self.assertContains(res, "leaflet.css")
        self.assertContains(res, "basemaps.cartocdn.com/rastertiles/voyager")
        self.assertContains(res, "bangladesh-map")

        # Check destination pins & title
        self.assertContains(res, "Explore Bangladesh Map")
        self.assertContains(res, "Sajek Valley")
        self.assertContains(res, "Cox&#x27;s Bazar")

        # Check embedded JSON
        self.assertContains(res, "destinations-data")

    def test_destination_map_api(self):
        """API endpoint delivers structured destination and tour package previews."""
        url = reverse('tours:map_destinations_api')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('destinations', data)
        dest_list = data['destinations']
        self.assertTrue(len(dest_list) >= 2)

        sajek_entry = next((d for d in dest_list if d['slug'] == 'sajek-valley'), None)
        self.assertIsNotNone(sajek_entry)
        self.assertAlmostEqual(sajek_entry['lat'], 23.3820, places=3)
        self.assertAlmostEqual(sajek_entry['lng'], 92.2938, places=3)
        self.assertEqual(sajek_entry['tours_count'], 1)
        self.assertEqual(sajek_entry['tours'][0]['title'], "Sajek Cloud Camp & Valley Escape")
        self.assertEqual(sajek_entry['tours'][0]['price'], 7500.0)

    def test_map_access_buttons_on_site(self):
        """Verify Map Access buttons are present on homepage, navbar, and footer."""
        # Check homepage
        home_res = self.client.get(reverse('core:home'))
        self.assertEqual(home_res.status_code, 200)
        self.assertContains(home_res, reverse('tours:interactive_map'))
        self.assertContains(home_res, "Explore Bangladesh Map")

        # Check map button in navbar
        self.assertContains(home_res, 'id="nav-btn-explore-map"')
        self.assertContains(home_res, 'id="btn-hero-explore-map"')
        self.assertContains(home_res, 'id="btn-home-visit-bangladesh-map"')
