from django.test import TestCase, Client
from django.urls import reverse

class Bug6NavbarAlignmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_navbar_centered_container_and_balanced_margins(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # 1. Header has #main-navbar
        self.assertIn('id="main-navbar"', content)

        # 2. Main navbar row uses centered max-w-screen-2xl mx-auto with equal side padding
        self.assertIn('max-w-screen-2xl w-full mx-auto px-4 sm:px-6 lg:px-8', content)

        # 3. Live clock utility bar also matches centered max-w-screen-2xl mx-auto
        self.assertIn('max-w-screen-2xl mx-auto flex items-center justify-between', content)

        # 4. Desktop nav has centered flex structure
        self.assertIn('hidden lg:flex items-center justify-center flex-1', content)

        # 5. Book a tour CTA button has flex-shrink-0 and is visible
        self.assertIn('Book a Tour', content)
        self.assertIn('flex-shrink-0', content)

        # 6. Check that old unbounded 1440px container is replaced
        self.assertNotIn('max-w-[1440px] w-full mx-auto', content)
