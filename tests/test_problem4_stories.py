from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.stories.models import Story, StoryImage
from apps.tours.models import Destination


class Problem4StorySubmissionAndModerationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin_tester', 'admin@example.com', 'adminpass123')
        self.destination = Destination.objects.create(name='Sajek Valley', description='Kingdom of Clouds')

        # Seed 1 approved story
        self.approved_story = Story.objects.create(
            title='Approved Adventure in Bandarban',
            content='This is an approved story that should be publicly visible.',
            destination=self.destination,
            status=Story.STATUS_APPROVED
        )

    def test_submit_story_form_get(self):
        """Verify the 'Share Your Story' form page loads with 200 OK."""
        response = self.client.get(reverse('stories:submit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'আপনার ভ্রমণ গল্প শেয়ার করুন')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="photos"')

    def test_user_submission_creates_pending_story_with_photos(self):
        """Verify user submissions are saved as 'pending' and photos attached."""
        # Create dummy test images
        img1 = SimpleUploadedFile("test1.jpg", b"dummy_content_1", content_type="image/jpeg")
        img2 = SimpleUploadedFile("test2.jpg", b"dummy_content_2", content_type="image/jpeg")

        post_data = {
            'title': 'My Epic Trek to Sajek',
            'destination': self.destination.id,
            'author_name': 'Kamal Hossain',
            'author_email': 'kamal@example.com',
            'content': 'We started our journey from Dhaka to Khagrachhari...',
            'photos': [img1, img2],
        }

        response = self.client.post(reverse('stories:submit'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ধন্যবাদ! আপনার ভ্রমণ গল্পটি সফলভাবে জমা হয়েছে')

        # Check DB
        story = Story.objects.filter(title='My Epic Trek to Sajek').first()
        self.assertIsNotNone(story)
        self.assertEqual(story.status, Story.STATUS_PENDING)
        self.assertEqual(story.author_name, 'Kamal Hossain')
        # Check attached images
        self.assertEqual(story.images.count(), 2)

    def test_pending_story_hidden_from_public_website(self):
        """Verify pending story is hidden from public list and home page."""
        pending_story = Story.objects.create(
            title='Secret Pending Story',
            content='This content must remain hidden from anonymous users.',
            destination=self.destination,
            status=Story.STATUS_PENDING
        )

        # Public stories list
        response = self.client.get(reverse('stories:list'))
        self.assertContains(response, self.approved_story.title)
        self.assertNotContains(response, pending_story.title)

        # Public home page
        home_response = self.client.get(reverse('core:home'))
        self.assertNotContains(home_response, pending_story.title)

        # Anonymous user accessing pending story detail directly gets 404
        detail_response = self.client.get(reverse('stories:detail', kwargs={'slug': pending_story.slug}))
        self.assertEqual(detail_response.status_code, 404)

    def test_admin_can_preview_and_approve_pending_story(self):
        """Verify admin can preview and approve pending story, making it live."""
        pending_story = Story.objects.create(
            title='Awesome Haor Journey',
            content='Sunamganj boat trip was magical.',
            destination=self.destination,
            status=Story.STATUS_PENDING
        )

        # Admin logs in
        self.client.login(username='admin_tester', password='adminpass123')

        # Admin CAN view pending story detail preview
        preview_response = self.client.get(reverse('stories:detail', kwargs={'slug': pending_story.slug}))
        self.assertEqual(preview_response.status_code, 200)
        self.assertContains(preview_response, 'Awesome Haor Journey')
        self.assertContains(preview_response, 'অনুমোদন করুন')

        # Admin approves the story
        approve_url = reverse('stories:moderate', kwargs={'story_id': pending_story.id, 'action': 'approve'})
        moderate_response = self.client.get(approve_url)
        self.assertEqual(moderate_response.status_code, 302)

        # Story status is now APPROVED
        pending_story.refresh_from_db()
        self.assertEqual(pending_story.status, Story.STATUS_APPROVED)

        # Now publicly visible
        self.client.logout()
        public_list_response = self.client.get(reverse('stories:list'))
        self.assertContains(public_list_response, 'Awesome Haor Journey')

    def test_admin_direct_posting_defaults_to_approved(self):
        """Verify admin direct posting saves story with approved status directly."""
        direct_story = Story.objects.create(
            title='Admin Direct Official Guide',
            content='Directly published article by admin.',
            destination=self.destination,
            status=Story.STATUS_APPROVED
        )
        self.assertEqual(direct_story.status, Story.STATUS_APPROVED)

        response = self.client.get(reverse('stories:list'))
        self.assertContains(response, 'Admin Direct Official Guide')
