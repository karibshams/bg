from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import SiteSetting
import os


class Problem1LogoAndTranslatorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.setting = SiteSetting.load()
        self.setting.phone = "+8801518919370, 01855939459"
        self.setting.email = "bhromonghuri@gmail.com"
        self.setting.facebook_url = "https://www.facebook.com/share/g/19km9RqB1g/"
        self.setting.save()

    def test_logo_navbar_asset_exists(self):
        """Verify that the optimized high-clarity logo exists in static images."""
        logo_path = os.path.join('static', 'images', 'logo-navbar.png')
        self.assertTrue(os.path.exists(logo_path), "logo-navbar.png does not exist in static/images/")
        self.assertGreater(os.path.getsize(logo_path), 0, "logo-navbar.png is empty")

    def test_navbar_logo_rendered_on_homepage(self):
        """Verify that the navbar renders the clear logo image instead of squashed graphic."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Navbar should use logo-navbar.png
        self.assertIn('logo-navbar.png', content)
        # Drop shadow and proper classes
        self.assertIn('h-11 sm:h-12 w-auto', content)

    def test_language_translator_ui_elements(self):
        """Verify the presence of the language translator dropdown and options in navbar."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Translator controls
        self.assertIn('language-dropdown-menu', content)
        self.assertIn('setSiteLanguage(\'en\')', content)
        self.assertIn('setSiteLanguage(\'bn\')', content)
        self.assertIn('English', content)
        self.assertIn('বাংলা', content)

        # Mobile drawer language switcher
        self.assertIn('language-mobile-menu', content)

        # Translator JS script loaded
        self.assertIn('translator.js', content)

    def test_contact_info_updated_from_pdf_specs(self):
        """Verify contact phone, email, and Facebook group link match PDF specs."""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('+8801518919370', content)
        self.assertIn('01855939459', content)
        self.assertIn('bhromonghuri@gmail.com', content)
        self.assertIn('https://maps.app.goo.gl/Cv52esJKLkZu2ouj9', content)
        self.assertIn('https://www.facebook.com/share/g/19km9RqB1g/', content)

    def test_navbar_spacing_and_responsiveness(self):
        """Verify balanced spacing, gap controls, and responsive classes across nav items."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Outer container has expanded max-width and balanced gap
        self.assertIn('max-w-[1440px]', content)
        # Desktop nav has balanced gaps and prevents awkward line breaking
        self.assertIn('whitespace-nowrap', content)
        self.assertIn('justify-center', content)
        # Responsive padding on nav items
        self.assertIn('px-2.5 py-1.5 xl:px-3.5 xl:py-2', content)
        # Header actions have balanced spacing
        self.assertIn('gap-2 lg:gap-2 xl:gap-3', content)
