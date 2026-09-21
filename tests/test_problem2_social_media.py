from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import SiteSetting


class Problem2SocialMediaIconsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.setting = SiteSetting.load()
        self.setting.facebook_url = "https://www.facebook.com/share/g/19km9RqB1g/"
        self.setting.instagram_url = "https://instagram.com/bhromonghuri"
        self.setting.youtube_url = "https://youtube.com/@bhromonghuri"
        self.setting.save()

    def test_footer_social_media_icons_visible(self):
        """Verify footer renders recognizable, high-visibility social media SVGs."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Check Facebook group link and SVG
        self.assertIn('https://www.facebook.com/share/g/19km9RqB1g/', content)
        self.assertIn('aria-label="Facebook Group"', content)

        # Check Instagram link and SVG
        self.assertIn('https://instagram.com/bhromonghuri', content)
        self.assertIn('aria-label="Instagram"', content)

        # Check YouTube link and SVG
        self.assertIn('https://youtube.com/@bhromonghuri', content)
        self.assertIn('aria-label="YouTube"', content)

        # Check WhatsApp link
        self.assertIn('wa.me/8801518919370', content)
        self.assertIn('aria-label="WhatsApp Helpline"', content)

    def test_contact_page_social_media_section(self):
        """Verify contact page has clearly visible social media section."""
        response = self.client.get(reverse('core:contact'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('সোশ্যাল মিডিয়ায় যুক্ত থাকুন / Connect With Us', content)
        self.assertIn('https://www.facebook.com/share/g/19km9RqB1g/', content)
        self.assertIn('https://instagram.com/bhromonghuri', content)
        self.assertIn('wa.me/8801518919370', content)

    def test_about_page_social_media_section(self):
        """Verify about page has community social media section."""
        response = self.client.get(reverse('core:about'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('ভ্রমণঘুড়ি পরিবারের সাথে যুক্ত থাকুন', content)
        self.assertIn('https://www.facebook.com/share/g/19km9RqB1g/', content)
        self.assertIn('https://instagram.com/bhromonghuri', content)

    def test_mobile_navbar_drawer_social_icons(self):
        """Verify mobile navigation drawer includes quick social media links."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Navbar should contain mobile social media container
        self.assertIn('Mobile Social Links', content)
