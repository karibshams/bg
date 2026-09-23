from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import os
import urllib.parse


class Problem2GoogleOAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_mock_form_and_hardcoded_credentials_completely_removed(self):
        """Verify hardcoded 'shams22karib@gmail.com' and 'Karib Shams' are absent site-wide."""
        for url_name in ['core:login', 'core:register', 'core:google_login']:
            response = self.client.get(reverse(url_name))
            content = response.content.decode('utf-8')
            self.assertNotIn('shams22karib@gmail.com', content, f"Hardcoded email found in {url_name}")
            self.assertNotIn('Karib Shams', content, f"Hardcoded name found in {url_name}")
            self.assertNotIn('Sign In as Karib Shams', content, f"Hardcoded sign-in button found in {url_name}")

    def test_fake_email_forms_removed_from_login_and_register(self):
        """Ensure no arbitrary email input forms post directly to google_login."""
        for url_name, expected_button in [('core:login', 'Continue with Google'), ('core:register', 'Sign up with Google')]:
            response = self.client.get(reverse(url_name))
            content = response.content.decode('utf-8')
            self.assertNotIn(f'action="{reverse("core:google_login")}"', content)
            self.assertIn(expected_button, content)

    @patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'test-google-client-id-12345.apps.googleusercontent.com'})
    def test_google_login_redirects_directly_to_google_oauth_endpoint(self):
        """Verify clicking Google Sign-In initiates official Google OAuth 2.0 flow."""
        response = self.client.get(reverse('core:google_login'))
        self.assertEqual(response.status_code, 302)
        redirect_url = response.url

        # Check target host
        self.assertTrue(redirect_url.startswith('https://accounts.google.com/o/oauth2/v2/auth'))

        parsed = urllib.parse.urlparse(redirect_url)
        params = urllib.parse.parse_qs(parsed.query)

        # Verify Google OAuth 2.0 parameters
        self.assertEqual(params['client_id'], ['test-google-client-id-12345.apps.googleusercontent.com'])
        self.assertIn('/auth/google/callback/', params['redirect_uri'][0])
        self.assertEqual(params['response_type'], ['code'])
        self.assertEqual(params['scope'], ['openid email profile'])
        self.assertEqual(params['prompt'], ['select_account'])
        self.assertIn('state', params)

    def test_post_bypass_removed_from_google_login(self):
        """Ensure POSTing arbitrary fake credentials to google_login no longer creates/authenticates user."""
        response = self.client.post(reverse('core:google_login'), {
            'email': 'fake.unverified@gmail.com',
            'name': 'Fake Traveler'
        })
        # Should not create fake user
        self.assertFalse(User.objects.filter(email='fake.unverified@gmail.com').exists())
        # Session should not be authenticated
        self.assertNotIn('_auth_user_id', self.client.session)

    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('apps.core.views.requests.post')
    @patch('apps.core.views.requests.get')
    def test_authentic_verified_google_user_instant_registration_and_login(self, mock_get, mock_post):
        """Verify authentic Google account with verified email is instantly registered and signed in without admin approval."""
        # Setup session state
        session = self.client.session
        session['oauth_state'] = 'secure-random-state-xyz'
        session['auth_next'] = reverse('core:home')
        session.save()

        # Mock token exchange
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {'access_token': 'mock-access-token-123'}
        mock_post.return_value = mock_token_resp

        # Mock userinfo with VERIFIED email
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            'email': 'authentic.traveler@gmail.com',
            'email_verified': True,
            'given_name': 'Authentic',
            'family_name': 'Traveler',
            'name': 'Authentic Traveler'
        }
        mock_get.return_value = mock_userinfo_resp

        response = self.client.get(reverse('core:google_callback'), {
            'code': 'valid-google-auth-code',
            'state': 'secure-random-state-xyz'
        }, follow=True)

        self.assertEqual(response.status_code, 200)

        # User must be created, active immediately (no admin approval needed)
        user = User.objects.filter(email='authentic.traveler@gmail.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_active)
        self.assertEqual(user.first_name, 'Authentic')

        # User is authenticated in current session
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    @patch.dict(os.environ, {
        'GOOGLE_CLIENT_ID': 'test-client-id',
        'GOOGLE_CLIENT_SECRET': 'test-client-secret'
    })
    @patch('apps.core.views.requests.post')
    @patch('apps.core.views.requests.get')
    def test_strict_email_verification_blocks_unverified_google_email(self, mock_get, mock_post):
        """Verify accounts with unverified email addresses are strictly blocked and rejected."""
        session = self.client.session
        session['oauth_state'] = 'state-abc'
        session.save()

        # Mock token exchange
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {'access_token': 'mock-token'}
        mock_post.return_value = mock_token_resp

        # Mock userinfo with UNVERIFIED email
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            'email': 'unverified.spammer@gmail.com',
            'email_verified': False,
            'name': 'Unverified User'
        }
        mock_get.return_value = mock_userinfo_resp

        response = self.client.get(reverse('core:google_callback'), {
            'code': 'auth-code',
            'state': 'state-abc'
        }, follow=True)

        # Unverified user must NOT be created or logged in
        self.assertFalse(User.objects.filter(email='unverified.spammer@gmail.com').exists())
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_cancelled_google_login_handled_gracefully(self):
        """Verify user cancellation at Google prompt is handled cleanly with error message."""
        response = self.client.get(reverse('core:google_callback'), {
            'error': 'access_denied'
        }, follow=True)
        self.assertRedirects(response, reverse('core:login'))
