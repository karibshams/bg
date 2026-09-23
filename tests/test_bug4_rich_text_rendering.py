from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Tour, TourCategory, Destination, TourItinerary, parse_rich_text_items
from django.core.files.uploadedfile import SimpleUploadedFile

class Bug4RichTextRenderingTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = TourCategory.objects.create(name="Trek", slug="trek")
        self.destination = Destination.objects.create(
            name="Chittagong",
            slug="chittagong",
            description="Scenic Chittagong hill tracts and coastal area"
        )
        dummy_image = SimpleUploadedFile(
            name='sitakunda_cover.jpg',
            content=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9',
            content_type='image/jpeg'
        )
        self.tour = Tour.objects.create(
            title="Sitakunda Rich Text Tour",
            slug="sitakunda-rich-text-tour",
            category=self.category,
            destination=self.destination,
            price=2500,
            duration_days=2,
            description="<p>Welcome to the <strong>Sitakunda</strong> mountain trail!</p><p>Enjoy the breathtaking waterfalls.</p>",
            bangla_description="<p><strong>সীতাকুণ্ড</strong> পাহাড়ি ট্রেইলে স্বাগতম!</p>",
            included_items="<ul><li>Round-trip AC Bus</li><li>Breakfast and Lunch</li></ul>",
            excluded_items="<p>Personal expenses</p><p>Optional boating fee</p>",
            cover_image=dummy_image
        )
        TourItinerary.objects.create(
            tour=self.tour,
            day_number=1,
            title="Day 1 - Chandranath Hill Trek",
            description="<p>Climb the scenic <em>Chandranath Temple</em> stairs and enjoy <strong>panoramic views</strong>.</p>"
        )

    def test_parse_rich_text_items_helper(self):
        # Test 1: HTML list
        html_list = "<ul><li>• AC Transport</li><li>✓ Hotel Stay</li></ul>"
        items = parse_rich_text_items(html_list)
        self.assertEqual(items, ["AC Transport", "Hotel Stay"])

        # Test 2: Paragraph tags
        html_p = "<p>Mineral Water</p><p>• Entry Tickets</p>"
        items_p = parse_rich_text_items(html_p)
        self.assertEqual(items_p, ["Mineral Water", "Entry Tickets"])

        # Test 3: Plain text with bullets
        plain = "• Guide Service\n* First Aid Kit"
        items_plain = parse_rich_text_items(plain)
        self.assertEqual(items_plain, ["Guide Service", "First Aid Kit"])

    def test_tour_included_and_excluded_lists(self):
        included = self.tour.get_included_list()
        self.assertIn("Round-trip AC Bus", included)
        self.assertIn("Breakfast and Lunch", included)
        # Ensure no raw <li> or <ul> tags in parsed items
        for item in included:
            self.assertNotIn("<li>", item)
            self.assertNotIn("</li>", item)
            self.assertNotIn("<ul>", item)

        excluded = self.tour.get_excluded_list()
        self.assertIn("Personal expenses", excluded)
        self.assertIn("Optional boating fee", excluded)
        for item in excluded:
            self.assertNotIn("<p>", item)
            self.assertNotIn("</p>", item)

    def test_detail_view_renders_rich_text_without_escaping(self):
        url = reverse('tours:detail', kwargs={'slug': self.tour.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # The HTML tags should be rendered directly, NOT escaped as &lt;p&gt; or &lt;strong&gt;
        self.assertIn("<p>Welcome to the <strong>Sitakunda</strong> mountain trail!</p>", content)
        self.assertNotIn("&lt;p&gt;Welcome to the", content)

        # Itinerary rich text should also be unescaped
        self.assertIn("<em>Chandranath Temple</em>", content)
        self.assertNotIn("&lt;em&gt;Chandranath Temple&lt;/em&gt;", content)

        # Inclusions should be rendered cleanly
        self.assertIn("Round-trip AC Bus", content)
        self.assertNotIn("&lt;li&gt;Round-trip AC Bus&lt;/li&gt;", content)

        # Attribute data-html="true" should be present on the prose containers
        self.assertIn('data-html="true"', content)
