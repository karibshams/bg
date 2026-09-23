import os
from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour, TourCategory, TourDate
from apps.bookings.models import Booking


class Feature9ResponsivenessAndDeviceOptimizationTestCase(TestCase):
    """
    Test suite for Feature 9: Full Responsiveness & Device Optimization.
    Verifies that the entire website provides responsive layout, viewport configurations,
    safe area insets, touch scrolling, and zero layout overflow across mobile, tablet,
    laptop, and desktop screens.
    """

    def setUp(self):
        self.client = Client()
        self.destination = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            latitude=23.3822,
            longitude=92.2938,
            tagline="Kingdom of Clouds",
            description="Scenic cloud valley in Rangamati hill district."
        )
        self.category = TourCategory.objects.create(
            name="Adventure",
            bangla_name="রোমাঞ্চকর",
            slug="adventure"
        )
        self.tour = Tour.objects.create(
            title="Sajek Valley Expedition",
            bangla_title="সাজেক ভ্যালি অভিযান",
            slug="sajek-valley-expedition",
            destination=self.destination,
            category=self.category,
            price=8500,
            duration="3 Days / 2 Nights",
            duration_days=3,
            max_travelers=25,
            is_featured=True
        )

    def test_viewport_meta_tag_in_base_template(self):
        """Verify that base template contains standard mobile viewport tag."""
        res = self.client.get(reverse('core:home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1.0">', content)
        self.assertIn('overflow-x-hidden', content)
        self.assertIn('w-full max-w-full', content)

    def test_global_responsive_css_rules_in_main_css(self):
        """Verify that static/css/main.css includes mobile touch, media containment, and safe area rules."""
        css_path = os.path.join('static', 'css', 'main.css')
        self.assertTrue(os.path.exists(css_path), "main.css must exist")
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        self.assertIn('-webkit-text-size-adjust: 100%;', css_content)
        self.assertIn('touch-action: manipulation;', css_content)
        self.assertIn('-webkit-overflow-scrolling: touch;', css_content)
        self.assertIn('safe-area-bottom', css_content)
        self.assertIn('responsive-scroll-x', css_content)

    def test_hero_section_responsive_wrapping(self):
        """Verify that hero CTAs, search bar, and badges use responsive flex/grid wrapping."""
        res = self.client.get(reverse('core:home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('id="hero-cta-group"', content)
        self.assertIn('flex-wrap', content)
        self.assertIn('gap-3', content)
        self.assertIn('btn-hero-explore-map', content)

    def test_mobile_drawer_navigation_responsiveness(self):
        """Verify that mobile navigation drawer has max-height and scrolling for landscape mode."""
        res = self.client.get(reverse('core:home'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('max-h-[calc(100vh-4.5rem)]', content)
        self.assertIn('overflow-y-auto', content)
        self.assertIn('language-mobile-menu', content)

    def test_interactive_map_responsiveness_and_touch_pills(self):
        """Verify that interactive Bangladesh map has dynamic heights and mobile preview auto-scroll."""
        res = self.client.get(reverse('tours:interactive_map'))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('bangladesh-map', content)
        self.assertIn('min-h-[380px]', content)
        self.assertIn('responsive-scroll-x', content)
        self.assertIn('destination-preview-card', content)
        self.assertIn('scrollIntoView', content)

    def test_tour_detail_mobile_sticky_booking_bar_and_clearance(self):
        """Verify that tour detail page provides mobile sticky bar with safe area clearance."""
        res = self.client.get(reverse('tours:detail', kwargs={'slug': self.tour.slug}))
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('pb-28 lg:pb-12', content)
        self.assertIn('safe-area-bottom', content)
        self.assertIn('lg:hidden fixed bottom-0', content)

    def test_booking_checkout_and_summary_responsiveness(self):
        """Verify that booking form scopes sticky sidebar to lg screens and stacks on mobile."""
        res = self.client.get(reverse('bookings:create') + f"?tour={self.tour.slug}")
        self.assertEqual(res.status_code, 200)
        content = res.content.decode('utf-8')

        self.assertIn('lg:col-span-5 lg:sticky lg:top-24', content)

    def test_bus_seat_diagram_horizontal_containment(self):
        """Verify that bus seat cabin diagram includes responsive-scroll-x containment."""
        template_path = os.path.join('templates', 'bookings', 'lookup.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        self.assertIn('responsive-scroll-x', template_content)
        self.assertIn('overflow-x-auto', template_content)

    def test_offline_booking_admin_responsive_grid(self):
        """Verify that offline desk booking admin template contains responsive-booking-grid style."""
        template_path = os.path.join('templates', 'admin', 'bookings', 'offline_booking_create.html')
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        self.assertIn('.offline-booking-grid', template_content)
        self.assertIn('@media (max-width: 992px)', template_content)
        self.assertIn('grid-template-columns: 1fr', template_content)

    def test_mobile_user_agent_headers_rendering(self):
        """Verify successful HTTP 200 responses when requesting pages as iPhone and Android user-agents."""
        user_agents = [
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1'
        ]

        pages = [
            reverse('core:home'),
            reverse('tours:list'),
            reverse('tours:interactive_map'),
            reverse('tours:detail', kwargs={'slug': self.tour.slug}),
            reverse('bookings:lookup'),
            reverse('core:contact'),
        ]

        for ua in user_agents:
            for page in pages:
                res = self.client.get(page, HTTP_USER_AGENT=ua)
                self.assertEqual(res.status_code, 200, f"Page {page} failed with UA {ua}")
