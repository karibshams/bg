from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from apps.core.models import EmailVerification
import os
import urllib.parse
from unittest.mock import patch, MagicMock


class Bug5DualAuthAndRecoveryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_password = "Password123!"

    def test_dual_auth_ui_rendered_on_login_and_register(self):
        # 1. Login page checks
        resp_login = self.client.get(reverse('core:login'))
        self.assertEqual(resp_login.status_code, 200)
        content_login = resp_login.content.decode('utf-8')

        # Option 1: Google SSO
        self.assertIn('Continue with Google', content_login)
        self.assertIn(reverse('core:google_login'), content_login)

        # Option 2: Manual Credentials Form
        self.assertIn('name="login_id"', content_login)
        self.assertIn('name="password"', content_login)
        self.assertIn('Forgot Password?', content_login)
        self.assertIn(reverse('core:forgot_password'), content_login)

        # 2. Register page checks
        resp_reg = self.client.get(reverse('core:register'))
        self.assertEqual(resp_reg.status_code, 200)
        content_reg = resp_reg.content.decode('utf-8')

        # Option 1: Google SSO
        self.assertIn('Sign up with Google', content_reg)

        # Option 2: Manual Registration Form
        self.assertIn('name="username"', content_reg)
        self.assertIn('name="email"', content_reg)
        self.assertIn('name="password"', content_reg)
        self.assertIn('name="password_confirm"', content_reg)

    @patch.dict(os.environ, {'GOOGLE_CLIENT_ID': 'bhromonghuri-test-client.apps.googleusercontent.com'})
    def test_google_oauth_initiates_direct_account_picker(self):
        resp = self.client.get(reverse('core:google_login'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('https://accounts.google.com/o/oauth2/v2/auth'))
        self.assertIn('client_id=bhromonghuri-test-client.apps.googleusercontent.com', resp.url)
        self.assertIn('prompt=select_account', resp.url)

    def test_manual_registration_requires_email_otp_activation(self):
        mail.outbox.clear()

        # Step 1: Submit manual registration
        resp = self.client.post(reverse('core:register'), {
            'username': 'tareq_traveler',
            'email': 'tareq.traveler@gmail.com',
            'password': self.test_password,
            'password_confirm': self.test_password
        })

        # Redirects to OTP verification page
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('core:verify_email'), resp.url)

        # User is created as inactive
        user = User.objects.get(email='tareq.traveler@gmail.com')
        self.assertFalse(user.is_active)

        # Verification OTP record is created
        ver = EmailVerification.objects.filter(email='tareq.traveler@gmail.com', purpose='register').first()
        self.assertIsNotNone(ver)
        self.assertEqual(len(ver.otp_code), 6)

        # Email was sent with OTP code
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ver.otp_code, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, ['tareq.traveler@gmail.com'])

        # Step 2: Attempt login while still unverified -> Should redirect to verify_email
        resp_login_fail = self.client.post(reverse('core:login'), {
            'login_id': 'tareq_traveler',
            'password': self.test_password
        })
        self.assertEqual(resp_login_fail.status_code, 302)
        self.assertIn(reverse('core:verify_email'), resp_login_fail.url)

        # Step 3: Enter wrong OTP code -> Fails
        resp_verify_wrong = self.client.post(reverse('core:verify_email'), {
            'email': 'tareq.traveler@gmail.com',
            'otp_code': '000000'
        })
        self.assertEqual(resp_verify_wrong.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

        # Step 4: Enter correct OTP code -> Activates user & logs in!
        latest_ver = EmailVerification.objects.filter(email='tareq.traveler@gmail.com', purpose='register', is_used=False).first()
        resp_verify_ok = self.client.post(reverse('core:verify_email'), {
            'email': 'tareq.traveler@gmail.com',
            'otp_code': latest_ver.otp_code
        })
        self.assertEqual(resp_verify_ok.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_direct_link_email_token_verification(self):
        user = User.objects.create_user(
            username='shamim_trekker',
            email='shamim.trekker@gmail.com',
            password=self.test_password,
            is_active=False
        )
        ver = EmailVerification.create_verification(user, purpose='register')

        url = f"{reverse('core:verify_email')}?email={ver.email}&token={ver.token}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_manual_login_with_username_and_email(self):
        active_user = User.objects.create_user(
            username='jahid_explorer',
            email='jahid.explorer@gmail.com',
            password=self.test_password,
            is_active=True
        )

        # 1. Login with username
        resp1 = self.client.post(reverse('core:login'), {
            'login_id': 'jahid_explorer',
            'password': self.test_password
        })
        self.assertEqual(resp1.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), active_user.id)
        self.client.logout()

        # 2. Login with email
        resp2 = self.client.post(reverse('core:login'), {
            'login_id': 'jahid.explorer@gmail.com',
            'password': self.test_password
        })
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), active_user.id)

    def test_forgot_and_reset_password_recovery_flow(self):
        mail.outbox.clear()
        user = User.objects.create_user(
            username='nusrat_traveler',
            email='nusrat.traveler@gmail.com',
            password='OldPassword123',
            is_active=True
        )

        # Step 1: Request password reset via registered Gmail
        resp_forgot = self.client.post(reverse('core:forgot_password'), {
            'email': 'nusrat.traveler@gmail.com'
        })
        self.assertEqual(resp_forgot.status_code, 302)
        self.assertIn(reverse('core:reset_password'), resp_forgot.url)

        # Reset OTP generated and sent
        ver = EmailVerification.objects.filter(email='nusrat.traveler@gmail.com', purpose='reset_password').first()
        self.assertIsNotNone(ver)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(ver.otp_code, mail.outbox[0].body)

        # Step 2: Submit password reset form with valid OTP
        new_pass = "BrandNewSecret2026!"
        resp_reset = self.client.post(reverse('core:reset_password'), {
            'email': 'nusrat.traveler@gmail.com',
            'otp_code': ver.otp_code,
            'new_password': new_pass,
            'confirm_password': new_pass
        })
        self.assertEqual(resp_reset.status_code, 302)
        self.assertEqual(resp_reset.url, reverse('core:login'))

        # Step 3: Verify old password fails and new password succeeds
        user.refresh_from_db()
        self.assertFalse(user.check_password('OldPassword123'))
        self.assertTrue(user.check_password(new_pass))

        resp_login = self.client.post(reverse('core:login'), {
            'login_id': 'nusrat.traveler@gmail.com',
            'password': new_pass
        })
        self.assertEqual(resp_login.status_code, 302)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)
