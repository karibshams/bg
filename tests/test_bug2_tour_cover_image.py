from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from apps.tours.models import Tour, TourCategory, Destination
from apps.tours.admin import TourAdmin, TourAdminForm
from django.contrib import admin

User = get_user_model()

class TourCoverImageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_cover_test',
            email='admin_cover@bhromonghuri.com',
            password='testpassword123'
        )
        self.client.force_login(self.admin_user)

        self.category = TourCategory.objects.create(name='Hill Trek', slug='hill-trek')
        self.destination = Destination.objects.create(
            name='Sitakunda',
            slug='sitakunda',
            description='Sitakunda hills and water bodies'
        )
        
        # 1x1 test image
        self.dummy_image = SimpleUploadedFile(
            name='sitakunda_cover.jpg',
            content=b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9',
            content_type='image/jpeg'
        )

        self.tour = Tour.objects.create(
            title='Sitakunda Trail Experience',
            slug='sitakunda-trail-experience',
            category=self.category,
            destination=self.destination,
            price=Decimal('3500.00'),
            duration_days=1,
            cover_image=self.dummy_image
        )

    def test_tour_admin_form_requires_cover_image(self):
        """Verify that TourAdminForm enforces cover_image as mandatory."""
        form_data = {
            'title': 'New Tour Without Image',
            'slug': 'new-tour-without-image',
            'destination': self.destination.id,
            'category': self.category.id,
            'duration_type': 'DAY_TOUR',
            'duration_days': 1,
            'duration': '1 Day',
            'price': '2000.00',
            'max_travelers': 20,
            'short_description': 'Short description',
            'description': 'Full description'
        }
        form = TourAdminForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cover_image', form.errors)

    def test_tour_admin_has_cover_preview_and_thumbnail(self):
        """Verify TourAdmin has cover_thumbnail in list_display and cover_image_preview."""
        tour_admin = admin.site._registry[Tour]
        self.assertIn('cover_thumbnail', tour_admin.list_display)
        self.assertIn('cover_image_preview', tour_admin.readonly_fields)
        
        # Test thumbnail html rendering
        thumb_html = tour_admin.cover_thumbnail(self.tour)
        self.assertIn('<img', thumb_html)
        self.assertIn('sitakunda_cover', thumb_html)
        
        # Test preview html rendering
        preview_html = tour_admin.cover_image_preview(self.tour)
        self.assertIn('<img', preview_html)
        self.assertIn('Live Cover Preview', tour_admin.cover_image_preview.short_description)

    def test_tour_admin_add_view_displays_cover_image_fieldset(self):
        """Verify that the admin tour creation page prominently features the cover image field."""
        response = self.client.get('/admin/tours/tour/add/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('Tour Package Cover Image &amp; Media', content)
        self.assertIn('name="cover_image"', content)
        self.assertIn('Mandatory', content)

    def test_tour_detail_renders_custom_cover_image(self):
        """Verify that the tour detail page renders the uploaded cover image."""
        response = self.client.get(f'/tours/{self.tour.slug}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn(self.tour.cover_image.url, content)
