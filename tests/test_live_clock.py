import os
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

class LiveClockTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_clock_script_file_exists(self):
        clock_file_path = os.path.join(settings.BASE_DIR, 'static', 'js', 'clock.js')
        self.assertTrue(os.path.exists(clock_file_path), "clock.js must exist in static/js/")
        with open(clock_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("updateLiveClock", content)
        self.assertIn("toBanglaDigits", content)
        self.assertIn("live-time-display", content)
        self.assertIn("live-date-display", content)

    def test_navbar_renders_live_clock_widget(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="live-clock-widget"')
        self.assertContains(response, 'class="live-date-display')
        self.assertContains(response, 'class="live-time-display')
        self.assertContains(response, 'js/clock.js')

    def test_clock_elements_present_on_multiple_pages(self):
        pages = [
            reverse('core:home'),
            reverse('tours:list'),
            reverse('stories:list'),
            reverse('gallery:index'),
            reverse('core:about'),
            reverse('core:contact'),
        ]
        for url in pages:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Page {url} failed to load")
            self.assertContains(resp, 'live-time-display', msg_prefix=f"Missing clock on {url}")
            self.assertContains(resp, 'live-date-display', msg_prefix=f"Missing date on {url}")
