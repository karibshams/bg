from django.test import TestCase, Client
from django.urls import reverse
from apps.core.models import SiteSetting
from apps.tours.models import Destination, Tour
import os


class Problem3BilingualEnglishDefaultTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.setting = SiteSetting.load()
        self.setting.hero_headline = "Explore Unseen Bangladesh With Fresh Eyes"
        self.setting.hero_headline_bn = "অদেখা বাংলাকে নতুন চোখে দেখা"
        self.setting.hero_subheadline = "New places, new stories, new emotions"
        self.setting.hero_subheadline_bn = "নতুন জায়গা, নতুন গল্প, নতুন অনুভূতি"
        self.setting.save()

        self.destination = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley-test",
            tagline="Kingdom of Clouds",
            description="Experience breathtaking floating clouds.",
            bangla_description="মেঘের দেশে রোমাঞ্চকর ভ্রমণ।"
        )

        self.tour = Tour.objects.create(
            destination=self.destination,
            title="Sajek Cloud Kingdom Adventure",
            bangla_title="সাজেক ভ্যালি মেঘের দেশে অ্যাডভেঞ্চার",
            slug="sajek-cloud-kingdom-test",
            duration="3 Days / 2 Nights",
            price=9500,
            discount_price=8500,
            is_featured=True,
            is_published=True,
            short_description="3 Days immersive tour in the cloud realm.",
            bangla_short_description="৩ দিনের মেঘের রাজ্যে অনাবিল ভ্রমণ।"
        )

    def test_default_html_lang_attribute_is_english(self):
        """Verify that <html> renders lang='en' by default."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<html lang="en"', content)

    def test_navbar_default_language_indicator_is_en(self):
        """Verify navbar displays EN by default."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('current-lang-code font-semibold">EN</span>', content)

    def test_brand_logo_is_preserved_in_bengali(self):
        """Verify that brand logo 'ভ্রমণঘুড়ি' is untouched and kept in Bengali."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('aria-label="ভ্রমণঘুড়ি"', content)
        self.assertIn('alt="ভ্রমণঘুড়ি"', content)

    def test_homepage_renders_english_hero_by_default(self):
        """Verify that homepage renders English hero title and subtitle by default."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Explore Unseen Bangladesh With Fresh Eyes', content)
        self.assertIn('New places, new stories, new emotions', content)
        self.assertIn('EXPLORE OUR JOURNEYS', content)
        self.assertIn('Our Best Tour Packages', content)

    def test_tour_card_renders_english_defaults_with_bilingual_data(self):
        """Verify tour card displays English title with bilingual data attributes."""
        response = self.client.get(reverse('tours:list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Sajek Cloud Kingdom Adventure', content)
        self.assertIn('data-en="Sajek Cloud Kingdom Adventure"', content)
        self.assertIn('data-bn="সাজেক ভ্যালি মেঘের দেশে অ্যাডভেঞ্চার"', content)
        self.assertIn('View Details', content)
        self.assertIn('Price per person', content)

    def test_booking_lookup_renders_english_defaults(self):
        """Verify booking lookup page renders English default headings and form labels."""
        response = self.client.get(reverse('bookings:lookup'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Check Your Booking Status', content)
        self.assertIn('Booking Reference Number', content)
        self.assertIn('Search Booking', content)

    def test_booking_form_renders_english_defaults(self):
        """Verify new booking form renders English step titles and input labels."""
        response = self.client.get(f"{reverse('bookings:create')}?tour={self.tour.slug}")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn('Confirm Your Journey', content)
        self.assertIn('Selected Tour & Date', content)
        self.assertIn('Number of Travelers', content)
        self.assertIn('Customer Details', content)
        self.assertIn('Full Name *', content)
        self.assertIn('Proceed to Payment →', content)

    def test_about_and_contact_pages_render_english_defaults(self):
        """Verify About and Contact pages render English headings and content."""
        about_res = self.client.get(reverse('core:about'))
        self.assertEqual(about_res.status_code, 200)
        about_content = about_res.content.decode('utf-8')
        self.assertIn('Our Journey & Philosophy', about_content)
        self.assertIn('Safety First', about_content)

        contact_res = self.client.get(reverse('core:contact'))
        self.assertEqual(contact_res.status_code, 200)
        contact_content = contact_res.content.decode('utf-8')
        self.assertIn('Contact Our Travel Experts', contact_content)
        self.assertIn('BhromonGhuri Head Office', contact_content)

    def test_translator_js_logic_and_rules(self):
        """Verify translator.js sets English default, provides bidirectional dictionary, and excludes brand logo."""
        translator_path = os.path.join('static', 'js', 'translator.js')
        with open(translator_path, 'r', encoding='utf-8') as f:
            code = f.read()

        # English default
        self.assertIn("localStorage.getItem(STORAGE_KEY) || 'en'", code)
        # Brand logo protection
        self.assertIn("aria-label=\"ভ্রমণঘুড়ি\"", code)
        self.assertIn("brand-logo-text", code)
        # Bilingual target swapping
        self.assertIn("data-en", code)
        self.assertIn("data-bn", code)
        self.assertIn("data-en-placeholder", code)
        self.assertIn("data-bn-placeholder", code)
