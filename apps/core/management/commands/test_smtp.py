import sys
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Test SMTP email configuration by sending a verification/OTP test email."

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            nargs='?',
            type=str,
            default=None,
            help="Recipient email address (defaults to EMAIL_HOST_USER or DEFAULT_FROM_EMAIL)"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== BhromonGhuri SMTP Diagnostic & Test ==="))

        recipient = options.get('recipient')
        if not recipient:
            recipient = getattr(settings, 'EMAIL_HOST_USER', None) or 'bhromonghuri@gmail.com'

        # Display current configuration
        password_masked = "********" if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else "[NOT SET]"
        self.stdout.write(f"EMAIL_BACKEND   : {getattr(settings, 'EMAIL_BACKEND', 'Not set')}")
        self.stdout.write(f"EMAIL_HOST      : {getattr(settings, 'EMAIL_HOST', 'Not set')}")
        self.stdout.write(f"EMAIL_PORT      : {getattr(settings, 'EMAIL_PORT', 'Not set')}")
        self.stdout.write(f"EMAIL_USE_TLS   : {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
        self.stdout.write(f"EMAIL_USE_SSL   : {getattr(settings, 'EMAIL_USE_SSL', 'Not set')}")
        self.stdout.write(f"EMAIL_HOST_USER : {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
        self.stdout.write(f"EMAIL_HOST_PASS : {password_masked}")
        self.stdout.write(f"DEFAULT_FROM    : {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
        self.stdout.write(f"TEST RECIPIENT  : {recipient}")
        self.stdout.write("--------------------------------------------------")

        test_otp = "852963"
        subject = f"[BhromonGhuri SMTP Test] Verification OTP Code: {test_otp}"
        message = f"""ভ্রমণঘুড়িতে স্বাগতম!
This is a test verification email from BhromonGhuri SMTP Diagnostic tool.

Your Test OTP Code: {test_otp}
SMTP Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}:{getattr(settings, 'EMAIL_PORT', 'Not set')}

If you received this email, your SMTP configuration is fully active and functioning!
— Team BhromonGhuri
"""
        html_message = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: sans-serif; color: #f8fafc;">
  <div style="max-width: 500px; margin: 30px auto; background-color: #1e293b; border-radius: 12px; border: 1px solid #334155; padding: 24px; text-align: center;">
    <h2 style="color: #38bdf8; margin-top: 0;">🪁 BhromonGhuri SMTP Test</h2>
    <p style="color: #94a3b8; font-size: 14px;">Your SMTP configuration is working properly!</p>
    <div style="background-color: #0f172a; border: 2px dashed #0ea5e9; border-radius: 10px; padding: 15px; margin: 20px 0;">
      <span style="font-size: 12px; color: #94a3b8; display: block; margin-bottom: 5px;">TEST VERIFICATION OTP</span>
      <span style="font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #38bdf8; font-family: monospace;">{test_otp}</span>
    </div>
    <p style="color: #64748b; font-size: 12px;">Sent from {getattr(settings, 'EMAIL_HOST', 'SMTP Server')}</p>
  </div>
</body>
</html>"""

        self.stdout.write(f"Attempting to send test email to {recipient}...")
        try:
            sent_count = send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False
            )
            if sent_count > 0:
                self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Test OTP email sent successfully to {recipient}!"))
            else:
                self.stdout.write(self.style.WARNING("[WARNING] send_mail returned 0 sent messages."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[FAILED] Failed to send email: {e}"))
            self.stdout.write(self.style.NOTICE(
                "\nTroubleshooting tips:\n"
                "1. If using Gmail, make sure 2-Step Verification is ON and you generated an App Password (16 letters, not account password).\n"
                "2. Ensure port 587 (TLS) or 465 (SSL) is allowed through your network firewall.\n"
                "3. Check your credentials in .env file (EMAIL_HOST_USER and EMAIL_HOST_PASSWORD)."
            ))
            sys.exit(1)
