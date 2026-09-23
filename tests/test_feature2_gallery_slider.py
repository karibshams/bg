from django.test import TestCase, Client
from django.urls import reverse
from apps.tours.models import Destination, Tour
from apps.gallery.models import GalleryItem
from apps.core.views import get_home_context

class Feature2GallerySliderTestCase(TestCase):
    """
    Test suite for New Feature 2: Dynamic Photo Gallery Slider:
    - Dynamic Site-Wide Images: Pull every photo from the website's gallery sequentially.
    - Labels & Titles: Display the specific title and relevant details (e.g., destination name and category tag) alongside each image.
    - Sequential Display: Showcase photos one by one in an organized slider/carousel view.
    - Dedicated Gallery Page: Includes interactive sequential slider with View Switcher (Slider View / Grid View).
    """

    def setUp(self):
        self.client = Client()
        self.dest_sajek = Destination.objects.create(
            name="Sajek Valley",
            bangla_name="সাজেক ভ্যালি",
            slug="sajek-valley",
            description="Kingdom of clouds"
        )
        self.dest_bandarban = Destination.objects.create(
            name="Bandarban",
            bangla_name="বান্দরবান",
            slug="bandarban",
            description="Roof of Bangladesh"
        )
        self.tour_sajek = Tour.objects.create(
            title="Sajek Cloud Camp Tour",
            slug="sajek-cloud-camp",
            destination=self.dest_sajek,
            price=8000.00,
            duration="3 Days",
            duration_days=3,
            is_published=True
        )

        # Create multiple gallery items across different categories and destinations
        self.item1 = GalleryItem.objects.create(
            title="Morning Mist Over Sajek Helipad",
            bangla_title="সাজেকের হেলিপ্যাডে সকালের কুয়াশা",
            destination=self.dest_sajek,
            tour=self.tour_sajek,
            category="MOUNTAIN",
            caption="Sunrise rays dancing across sea of clouds.",
            bangla_caption="মেঘের সমুদ্রে সূর্যোদয়ের প্রথম আলো।",
            order=1,
            is_featured=True
        )
        self.item2 = GalleryItem.objects.create(
            title="Golden Sunset Over Nilgiri",
            bangla_title="নীলগিরিতে সোনালী সূর্যাস্ত",
            destination=self.dest_bandarban,
            category="MOUNTAIN",
            caption="Dusk falling upon the hills of Bandarban.",
            bangla_caption="বান্দরবানের পাহাড়ে গোধূলির মায়াবী আলো।",
            order=2,
            is_featured=False  # Should still be pulled in full gallery slider!
        )
        self.item3 = GalleryItem.objects.create(
            title="Houseboat Journey in Tanguar Haor",
            bangla_title="টাঙ্গুয়ার হাওরে কাঠের বজরায় ভ্রমণ",
            category="GROUP",
            caption="Joyful evening with friends on emerald waters.",
            order=3,
            is_featured=False
        )

    def test_gallery_item_fields_and_relationships(self):
        """Test GalleryItem attributes including bilingual fields and tour relation."""
        self.assertEqual(self.item1.title, "Morning Mist Over Sajek Helipad")
        self.assertEqual(self.item1.bangla_title, "সাজেকের হেলিপ্যাডে সকালের কুয়াশা")
        self.assertEqual(self.item1.destination, self.dest_sajek)
        self.assertEqual(self.item1.tour, self.tour_sajek)
        self.assertEqual(self.item1.category, "MOUNTAIN")
        self.assertEqual(self.item1.order, 1)

    def test_home_context_pulls_all_gallery_photos_sequentially(self):
        """Verify home view pulls all photos from the gallery sequentially ordered by order."""
        context = get_home_context()
        gallery_items = list(context['gallery_items'])
        total_in_db = GalleryItem.objects.count()

        # Must pull EVERY photo from the gallery, not just first 6 or only is_featured
        self.assertEqual(len(gallery_items), total_in_db)
        # Sequential order check
        self.assertEqual(gallery_items[0].id, self.item1.id)
        self.assertEqual(gallery_items[1].id, self.item2.id)
        self.assertEqual(gallery_items[2].id, self.item3.id)

    def test_homepage_slider_renders_one_by_one_with_labels_and_titles(self):
        """Test homepage renders dynamic sequential photo gallery slider with all required labels."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        # Slider container & Alpine.js carousel state
        self.assertIn("EXCLUSIVE PHOTO GALLERY", content)
        self.assertIn("Memories of Beautiful Bangladesh", content)
        self.assertIn("x-data=\"{", content)
        self.assertIn("next()", content)
        self.assertIn("prev()", content)
        self.assertIn("goTo(", content)

        # Titles and relevant details alongside images
        self.assertIn("Morning Mist Over Sajek Helipad", content)
        self.assertIn("Golden Sunset Over Nilgiri", content)
        self.assertIn("Houseboat Journey in Tanguar Haor", content)
        self.assertIn("Sajek Valley", content)
        self.assertIn("Bandarban", content)
        self.assertIn("Mountains &amp; Hills", content)  # HTML-escaped &
        self.assertIn("Sunrise rays dancing across sea of clouds.", content)

        # Navigation controls & Filmstrip
        self.assertIn("Previous Photo", content)
        self.assertIn("Next Photo", content)
        self.assertIn("Full View", content)
        self.assertIn("Click any photo thumbnail to jump to slide:", content)

    def test_gallery_page_renders_slider_and_view_mode_switcher(self):
        """Test /gallery/ renders sequential slider and View Mode Switcher."""
        response = self.client.get(reverse('gallery:index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        self.assertIn("Slider View", content)
        self.assertIn("Grid View", content)
        self.assertIn("viewMode = 'slider'", content)
        self.assertIn("viewMode = 'grid'", content)
        self.assertIn("Morning Mist Over Sajek Helipad", content)
        self.assertIn("Sajek Valley", content)
