from django.test import TestCase, Client
from django.urls import reverse


class HeroNoBackgroundImageTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hero_does_not_use_background_image(self):
        """Hero container must not use any background image, maintaining atmospheric deep background."""
        resp = self.client.get(reverse('core:home'))
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')

        # Hero section exists
        self.assertIn('id="hero-section"', content)

        # No background image is applied to hero-section
        self.assertNotIn('hero-bg.jpg', content)

        # Atmospheric ambient glow & grid texture background is active
        self.assertIn('bg-slate-950', content)
        self.assertIn('radial-gradient', content)

        # Foreground UI elements are intact inside relative z-10
        self.assertIn('z-10', content)
        self.assertIn('id="hero-title"', content)
        self.assertIn('id="hero-subtitle"', content)
        self.assertIn('id="hero-search-form"', content)
        self.assertIn('id="hero-showcase"', content)
