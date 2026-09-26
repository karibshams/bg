import os
from pathlib import Path
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings


class HeroCustomBackgroundTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hero_background_asset_exists(self):
        """hero-bg.jpg asset must exist in static and public assets directory."""
        static_img = settings.BASE_DIR / 'static' / 'images' / 'hero-bg.jpg'
        self.assertTrue(static_img.exists(), "hero-bg.jpg must exist in static/images/")
        self.assertGreater(static_img.stat().st_size, 10000, "hero-bg.jpg should be valid non-empty image")

    def test_hero_background_and_dark_contrast_overlay_rendered(self):
        """Hero container must apply hero-bg.jpg with cover & center bottom, plus dark contrast gradient overlay."""
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')

        # 1. Background image integration
        self.assertIn('hero-bg.jpg', content)
        self.assertIn('background-size: cover', content)
        self.assertIn('background-position: center bottom', content)

        # 2. Dark contrast gradient overlay
        self.assertIn('rgba(5, 11, 24, 0.85)', content)
        self.assertIn('rgba(2, 6, 17, 0.92)', content)

        # 3. Foreground UI elements in relative z-10
        self.assertIn('z-10', content)
        self.assertIn('id="hero-title"', content)
        self.assertIn('id="hero-subtitle"', content)
        self.assertIn('id="hero-search-form"', content)
        self.assertIn('id="hero-showcase"', content)
