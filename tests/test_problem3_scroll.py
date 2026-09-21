from django.test import TestCase, Client
from django.urls import reverse
import os


class Problem3SmoothScrollTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_lenis_script_removed_from_base_html(self):
        """Verify that Lenis scroll hijacking script is removed from base template."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Lenis script should NOT be present in base.html
        self.assertNotIn('lenis.min.js', content)
        # GSAP and ScrollTrigger should still be present
        self.assertIn('gsap.min.js', content)
        self.assertIn('ScrollTrigger.min.js', content)

    def test_animations_js_does_not_hijack_wheel(self):
        """Verify animations.js does not initialize Lenis or intercept wheel events."""
        anim_path = os.path.join('static', 'js', 'animations.js')
        with open(anim_path, 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertNotIn('new Lenis', code)
        self.assertNotIn('smoothWheel', code)

    def test_main_js_uses_passive_scroll_listener(self):
        """Verify main.js uses a passive scroll listener with RAF to avoid blocking scroll thread."""
        main_path = os.path.join('static', 'js', 'main.js')
        with open(main_path, 'r', encoding='utf-8') as f:
            code = f.read()

        self.assertIn('{ passive: true }', code)
        self.assertIn('requestAnimationFrame', code)
