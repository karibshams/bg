from django.test import TestCase, Client
from django.urls import reverse

class Bug7CartoDBMapAndLocationSearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_map_uses_cartodb_voyager_tiles_and_zero_403_blocking(self):
        url = reverse('tours:interactive_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Tile source switched to CartoDB Voyager
        self.assertIn('basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', content)
        self.assertIn("subdomains: 'abcd'", content)

        # 2. Blocked tile.openstreetmap.org is completely removed
        self.assertNotIn('https://tile.openstreetmap.org/{z}/{x}/{y}.png', content)

    def test_map_initializes_with_bangladesh_bounds_and_center(self):
        url = reverse('tours:interactive_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Centered on Bangladesh [23.6850, 90.3563], zoom level 7
        self.assertIn('[23.6850, 90.3563]', content)
        self.assertIn('const initialZoom = 7;', content)

        # 2. Maximum panning bounds [[20.5, 88.0], [26.7, 92.7]]
        self.assertIn('[[20.5, 88.0], [26.7, 92.7]]', content)
        self.assertIn('maxBounds: bangladeshBounds', content)

    def test_bangladesh_location_search_bar_and_nominatim_integration(self):
        url = reverse('tours:interactive_map')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Search input and button exist
        self.assertIn('id="bd-location-search-input"', content)
        self.assertIn('id="btn-search-location"', content)
        self.assertIn('id="search-suggestions-dropdown"', content)

        # 2. Nominatim geocoding API with countrycodes=bd filter
        self.assertIn('nominatim.openstreetmap.org/search', content)
        self.assertIn('countrycodes=bd', content)

        # 3. Smooth flyTo animation to coordinates
        self.assertIn('map.flyTo', content)

    def test_map_api_key_configured(self):
        import os
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'MAP_API_KEY'))
        self.assertEqual(settings.MAP_API_KEY, os.getenv('MAP_API_KEY', ''))
