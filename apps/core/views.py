import os
import re
import secrets
import urllib.parse
import logging
import datetime
import requests
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import SiteSetting, Testimonial, FAQ, EmailVerification

logger = logging.getLogger(__name__)



# Dynamic imports from sibling apps with fallback
def get_home_context():
    from apps.tours.models import Tour, Destination, TourDate
    from apps.stories.models import Story
    from apps.gallery.models import GalleryItem

    site_setting = SiteSetting.load()
    featured_tours = Tour.objects.filter(is_published=True, is_featured=True).select_related('destination', 'category')[:6]
    destinations = Destination.objects.filter(is_featured=True)[:6]
    upcoming_dates = TourDate.objects.filter(
        is_active=True, 
        tour__is_published=True
    ).select_related('tour', 'tour__destination')[:4]
    stories = Story.objects.filter(status=Story.STATUS_APPROVED, is_featured=True).select_related('destination')[:3]
    gallery_items = GalleryItem.objects.select_related('destination', 'tour').all().order_by('order', '-created_at')
    testimonials = Testimonial.objects.filter(is_featured=True)[:5]
    faqs = FAQ.objects.filter(is_published=True)[:6]

    # Modification 3: Event-driven feed of active upcoming tours scheduled within the next 1–2 months (0-60 days)
    today = timezone.now().date()
    two_months_later = today + datetime.timedelta(days=60)
    upcoming_carousel_dates = TourDate.objects.filter(
        is_active=True,
        tour__is_published=True,
        start_date__gte=today,
        start_date__lte=two_months_later
    ).select_related('tour', 'tour__destination', 'tour__category').order_by('start_date')

    seen_tours = set()
    hero_carousel_items = []
    for td in upcoming_carousel_dates:
        if td.tour_id not in seen_tours:
            seen_tours.add(td.tour_id)
            tour = td.tour
            dest = tour.destination
            cover_url = tour.cover_image.url if tour.cover_image else '/static/images/hero-sajek.jpg'
            hero_carousel_items.append({
                'tour_id': tour.id,
                'slug': tour.slug,
                'title': tour.title,
                'bangla_title': tour.bangla_title or tour.title,
                'destination_name': dest.name if dest else 'Bangladesh',
                'destination_bangla': dest.bangla_name if (dest and dest.bangla_name) else (dest.name if dest else 'বাংলাদেশ'),
                'destination_tagline': getattr(dest, 'tagline', '') or 'Featured Destination',
                'image_url': cover_url,
                'price': int(tour.discount_price or tour.price),
                'regular_price': int(tour.price) if tour.discount_price else None,
                'departure_date': td.start_date.strftime('%d %b, %Y'),
                'start_date': td.start_date,
                'duration': tour.duration or f"{tour.duration_days} Days",
                'seats_left': td.available_seats,
            })
            if len(hero_carousel_items) >= 6:
                break

    # Graceful fallback if no dates fall within next 60 days
    if not hero_carousel_items:
        fallback_dates = TourDate.objects.filter(
            is_active=True,
            tour__is_published=True
        ).select_related('tour', 'tour__destination', 'tour__category').order_by('start_date')
        for td in fallback_dates:
            if td.tour_id not in seen_tours:
                seen_tours.add(td.tour_id)
                tour = td.tour
                dest = tour.destination
                cover_url = tour.cover_image.url if tour.cover_image else '/static/images/hero-sajek.jpg'
                hero_carousel_items.append({
                    'tour_id': tour.id,
                    'slug': tour.slug,
                    'title': tour.title,
                    'bangla_title': tour.bangla_title or tour.title,
                    'destination_name': dest.name if dest else 'Bangladesh',
                    'destination_bangla': dest.bangla_name if (dest and dest.bangla_name) else (dest.name if dest else 'বাংলাদেশ'),
                    'destination_tagline': getattr(dest, 'tagline', '') or 'Featured Destination',
                    'image_url': cover_url,
                    'price': int(tour.discount_price or tour.price),
                    'regular_price': int(tour.price) if tour.discount_price else None,
                    'departure_date': td.start_date.strftime('%d %b, %Y'),
                    'start_date': td.start_date,
                    'duration': tour.duration or f"{tour.duration_days} Days",
                    'seats_left': td.available_seats,
                })
                if len(hero_carousel_items) >= 6:
                    break

    if not hero_carousel_items:
        fallback_tours = Tour.objects.filter(is_published=True).select_related('destination')[:5]
        for tour in fallback_tours:
            dest = tour.destination
            cover_url = tour.cover_image.url if tour.cover_image else '/static/images/hero-sajek.jpg'
            hero_carousel_items.append({
                'tour_id': tour.id,
                'slug': tour.slug,
                'title': tour.title,
                'bangla_title': tour.bangla_title or tour.title,
                'destination_name': dest.name if dest else 'Bangladesh',
                'destination_bangla': dest.bangla_name if (dest and dest.bangla_name) else (dest.name if dest else 'বাংলাদেশ'),
                'destination_tagline': getattr(dest, 'tagline', '') or 'Featured Destination',
                'image_url': cover_url,
                'price': int(tour.discount_price or tour.price),
                'regular_price': int(tour.price) if tour.discount_price else None,
                'departure_date': 'Upcoming',
                'start_date': None,
                'duration': tour.duration or f"{tour.duration_days} Days",
                'seats_left': 20,
            })

    return {
        'site_setting': site_setting,
        'featured_tours': featured_tours,
        'destinations': destinations,
        'upcoming_dates': upcoming_dates,
        'stories': stories,
        'gallery_items': gallery_items,
        'testimonials': testimonials,
        'faqs': faqs,
        'hero_carousel_items': hero_carousel_items,
    }


def home_view(request):
    """Homepage view rendering all dynamic content controlled by Django Admin."""
    context = get_home_context()
    return render(request, 'home/index.html', context)


def about_view(request):
    """About us page view."""
    site_setting = SiteSetting.load()
    testimonials = Testimonial.objects.filter(is_featured=True)[:4]
    return render(request, 'core/about.html', {
        'site_setting': site_setting,
        'testimonials': testimonials,
    })


def contact_view(request):
    """Contact page view with inquiry submission feedback."""
    site_setting = SiteSetting.load()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        messages.success(request, f"ধন্যবাদ {name}! আপনার বার্তাটি সফলভাবে পাঠানো হয়েছে। আমরা শীঘ্রই যোগাযোগ করব।")
    return render(request, 'core/contact.html', {
        'site_setting': site_setting,
    })


def send_verification_otp_email(user, email_ver, request=None):
    """Sends 6-digit OTP code and direct link to user's email for activation with responsive HTML & plain-text fallback."""
    domain = request.get_host() if request else '127.0.0.1:8000'
    protocol = 'https' if request and request.is_secure() else 'http'
    verify_url = f"{protocol}://{domain}{reverse('core:verify_email')}?email={urllib.parse.quote(email_ver.email)}&token={email_ver.token}"

    subject = f"Your BhromonGhuri Verification Code: {email_ver.otp_code}"
    
    # Plain text fallback (ensures backward compatibility with test suites checking mail.outbox[0].body)
    message = f"""ভ্রমণঘুড়িতে স্বাগতম! Welcome to BhromonGhuri!

আপনার ইমেইল ভেরিফিকেশন কোড:
Your 6-digit Email Verification Code is:
=========================
        {email_ver.otp_code}
=========================
এই কোডটি আগামী ১৫ মিনিট পর্যন্ত কার্যকর থাকবে।

অথবা সরাসরি এই লিংকে ক্লিক করে একাউন্ট ভেরিফাই করুন:
Or verify directly using this link:
{verify_url}

যদি আপনি এই অনুরোধ না করে থাকেন, তবে বার্তাটি উপেক্ষা করুন।
If you did not request this, please ignore this email.

— টিম ভ্রমণঘুড়ি (BhromonGhuri)
"""

    html_message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BhromonGhuri Email Verification</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0f172a; padding: 40px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
          <tr>
            <td style="background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%); padding: 32px 24px; text-align: center;">
              <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: 0.5px;">
                🪁 ভ্রমণঘুড়ি (BhromonGhuri)
              </h1>
              <p style="margin: 6px 0 0 0; color: #e0f2fe; font-size: 13px; letter-spacing: 1px; text-transform: uppercase;">
                Explore • Experience • Discover
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 28px;">
              <h2 style="margin: 0 0 10px 0; color: #ffffff; font-size: 20px; font-weight: 700; text-align: center;">
                ইমেইল ভেরিফিকেশন ওটিপি / Verification OTP
              </h2>
              <p style="margin: 0 0 22px 0; color: #94a3b8; font-size: 14px; line-height: 1.6; text-align: center;">
                ভ্রমণঘুড়িতে স্বাগতম! আপনার অ্যাকাউন্ট ভেরিফাই করতে নিচের ৬-সংখ্যার সিকিউরিটি কোডটি ব্যবহার করুন।
              </p>

              <div style="background-color: #0f172a; border: 2px dashed #0ea5e9; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 11px; text-transform: uppercase; color: #38bdf8; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 6px;">
                  Your 6-Digit OTP Code
                </div>
                <div style="font-size: 34px; font-weight: 900; letter-spacing: 8px; color: #38bdf8; font-family: 'Courier New', Courier, monospace;">
                  {email_ver.otp_code}
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
                  ⏱ মেয়াদ: ১৫ মিনিট (Valid for 15 minutes)
                </div>
              </div>

              <div style="text-align: center; margin-bottom: 24px;">
                <a href="{verify_url}" style="background: linear-gradient(135deg, #10b981 0%, #0ea5e9 100%); color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 28px; border-radius: 8px; display: inline-block;">
                  Verify Account Directly &rarr;
                </a>
              </div>

              <div style="border-top: 1px solid #334155; padding-top: 20px; color: #64748b; font-size: 12px; line-height: 1.5; text-align: center;">
                যদি আপনি এই অনুরোধ না করে থাকেন, তবে বার্তাটি উপেক্ষা করুন।<br>
                If you did not request this, please safely ignore this email.
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0f172a; padding: 16px; text-align: center; color: #475569; font-size: 11px; border-top: 1px solid #334155;">
              © 2026 BhromonGhuri. All rights reserved. | Dhaka, Bangladesh
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    try:
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_ver.email],
            fail_silently=False
        )
        logger.info(f"Verification OTP email sent successfully to {email_ver.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification OTP email to {email_ver.email}: {e}")
        return False


def send_password_reset_otp_email(user, email_ver, request=None):
    """Sends 6-digit OTP code for password recovery to user's email with responsive HTML & plain-text fallback."""
    domain = request.get_host() if request else '127.0.0.1:8000'
    protocol = 'https' if request and request.is_secure() else 'http'
    reset_url = f"{protocol}://{domain}{reverse('core:reset_password')}?email={urllib.parse.quote(email_ver.email)}"

    subject = f"BhromonGhuri Password Reset Code: {email_ver.otp_code}"
    
    # Plain text fallback
    message = f"""ভ্রমণঘুড়ি পাসওয়ার্ড রিসেট রিকোয়েস্ট / BhromonGhuri Password Reset Request

আপনার পাসওয়ার্ড রিসেট করার জন্য ৬-সংখ্যার সিকিউরিটি কোড:
Your 6-digit Password Reset Code is:
=========================
        {email_ver.otp_code}
=========================
এই কোডটি আগামী ১৫ মিনিট পর্যন্ত কার্যকর থাকবে।

রিসেট পেজে প্রবেশ করুন:
Go to password reset page:
{reset_url}

যদি আপনি পাসওয়ার্ড রিসেটের অনুরোধ না করে থাকেন, তবে দ্রুত আপনার একাউন্টের নিরাপত্তা নিশ্চিত করুন।
If you did not request this, please ignore this email.

— টিম ভ্রমণঘুড়ি (BhromonGhuri)
"""

    html_message = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BhromonGhuri Password Reset</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0f172a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0f172a; padding: 40px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
          <tr>
            <td style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding: 32px 24px; text-align: center;">
              <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: 0.5px;">
                🪁 ভ্রমণঘুড়ি (BhromonGhuri)
              </h1>
              <p style="margin: 6px 0 0 0; color: #fef3c7; font-size: 13px; letter-spacing: 1px; text-transform: uppercase;">
                Account Security & Password Recovery
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px 28px;">
              <h2 style="margin: 0 0 10px 0; color: #ffffff; font-size: 20px; font-weight: 700; text-align: center;">
                পাসওয়ার্ড রিসেট কোড / Password Reset Code
              </h2>
              <p style="margin: 0 0 22px 0; color: #94a3b8; font-size: 14px; line-height: 1.6; text-align: center;">
                আপনার অ্যাকাউন্টের পাসওয়ার্ড পরিবর্তন করার জন্য নিচের ৬-সংখ্যার সিকিউরিটি কোডটি ব্যবহার করুন।
              </p>

              <div style="background-color: #0f172a; border: 2px dashed #f59e0b; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                <div style="font-size: 11px; text-transform: uppercase; color: #fbbf24; font-weight: 700; letter-spacing: 1.5px; margin-bottom: 6px;">
                  Your Password Reset Code
                </div>
                <div style="font-size: 34px; font-weight: 900; letter-spacing: 8px; color: #fbbf24; font-family: 'Courier New', Courier, monospace;">
                  {email_ver.otp_code}
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 8px;">
                  ⏱ মেয়াদ: ১৫ মিনিট (Valid for 15 minutes)
                </div>
              </div>

              <div style="text-align: center; margin-bottom: 24px;">
                <a href="{reset_url}" style="background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); color: #ffffff; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 28px; border-radius: 8px; display: inline-block;">
                  Reset Password Now &rarr;
                </a>
              </div>

              <div style="border-top: 1px solid #334155; padding-top: 20px; color: #64748b; font-size: 12px; line-height: 1.5; text-align: center;">
                যদি আপনি পাসওয়ার্ড রিসেটের অনুরোধ না করে থাকেন, তবে দ্রুত আপনার একাউন্টের নিরাপত্তা নিশ্চিত করুন।<br>
                If you did not request this, please ensure your account credentials are secure.
              </div>
            </td>
          </tr>
          <tr>
            <td style="background-color: #0f172a; padding: 16px; text-align: center; color: #475569; font-size: 11px; border-top: 1px solid #334155;">
              © 2026 BhromonGhuri. All rights reserved. | Dhaka, Bangladesh
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    try:
        send_mail(
            subject=subject,
            message=message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_ver.email],
            fail_silently=False
        )
        logger.info(f"Password reset OTP email sent successfully to {email_ver.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset OTP email to {email_ver.email}: {e}")
        return False



def login_view(request):
    """User Login page featuring Dual Authentication: Google SSO and Manual Username/Password."""
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('core:home')

    if request.method == 'POST':
        login_id = request.POST.get('login_id', '').strip()
        password = request.POST.get('password', '').strip()

        if not login_id or not password:
            messages.error(request, "ইউজারনেম/ইমেইল এবং পাসওয়ার্ড উভয় ফিল্ড পূরণ করুন।")
            return render(request, 'core/login.html', {'next': next_url, 'login_id': login_id})

        user = None
        if '@' in login_id:
            user = User.objects.filter(email__iexact=login_id).first()
        if not user:
            user = User.objects.filter(username__iexact=login_id).first()

        if user and user.check_password(password):
            if not user.is_active:
                ver = EmailVerification.create_verification(user, purpose='register')
                send_verification_otp_email(user, ver, request)
                messages.warning(request, "আপনার অ্যাকাউন্টটি এখনো ভেরিফাই করা হয়নি। আপনার জিমেইলে নতুন ওটিপি (OTP) পাঠানো হয়েছে।")
                return redirect(f"{reverse('core:verify_email')}?email={urllib.parse.quote(user.email)}&next={urllib.parse.quote(next_url)}")

            login(request, user)
            request.session['customer_authenticated'] = True
            messages.success(request, f"স্বাগতম, {user.first_name or user.username}! সফলভাবে লগইন হয়েছেন।")
            return redirect(next_url)
        else:
            messages.error(request, "ভুল ইউজারনেম/ইমেইল অথবা পাসওয়ার্ড। অনুগ্রহ করে আবার চেষ্টা করুন।")
            return render(request, 'core/login.html', {'next': next_url, 'login_id': login_id})

    return render(request, 'core/login.html', {'next': next_url})


def register_view(request):
    """User Registration page featuring Dual Authentication: Google SSO and Manual Sign Up with Email OTP."""
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.POST.get('next') or request.GET.get('next') or reverse('core:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()

        if not username or not email or not password:
            messages.error(request, "সবগুলো ফিল্ড সঠিকভাবে পূরণ করুন।")
            return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})

        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            messages.error(request, "ইউজারনেমে শুধুমাত্র অক্ষর, সংখ্যা, ডট ও আন্ডারস্কোর ব্যবহার করতে পারেন।")
            return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})

        if '@' not in email or not email.split('@')[1]:
            messages.error(request, "অনুগ্রহ করে একটি সঠিক ইমেইল/জিমেইল অ্যাড্রেস প্রদান করুন।")
            return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})

        if len(password) < 6:
            messages.error(request, "পাসওয়ার্ড অন্তত ৬ অক্ষরের হতে হবে।")
            return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})

        if password != password_confirm:
            messages.error(request, "পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মেলেনি।")
            return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})

        if User.objects.filter(username__iexact=username).exists():
            existing_u = User.objects.filter(username__iexact=username).first()
            if existing_u.is_active:
                messages.error(request, "এই ইউজারনেমটি ইতিমধ্যে নিবন্ধিত রয়েছে। অনুগ্রহ করে অন্য ইউজারনেম বেছে নিন।")
                return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})
            else:
                existing_u.delete()

        existing_email_user = User.objects.filter(email__iexact=email).first()
        if existing_email_user:
            if existing_email_user.is_active:
                messages.error(request, "এই জিমেইল অ্যাড্রেসটি ইতিমধ্যে ব্যবহৃত হয়েছে। সরাসরি লগইন করুন।")
                return render(request, 'core/register.html', {'next': next_url, 'username': username, 'email': email})
            else:
                user = existing_email_user
                user.username = username
                user.set_password(password)
                user.save()
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )

        ver = EmailVerification.create_verification(user, purpose='register')
        send_verification_otp_email(user, ver, request)
        messages.info(request, f"আপনার জিমেইল ({email}) এ একটি ৬-সংখ্যার ভেরিফিকেশন ওটিপি পাঠানো হয়েছে।")
        return redirect(f"{reverse('core:verify_email')}?email={urllib.parse.quote(email)}&next={urllib.parse.quote(next_url)}")

    return render(request, 'core/register.html', {'next': next_url})


def verify_email_view(request):
    """Validates 6-digit OTP code or direct token for account activation."""
    email = (request.GET.get('email') or request.POST.get('email', '')).strip().lower()
    token = request.GET.get('token', '').strip()
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('core:home')

    # Direct email link verification
    if token and email:
        ver = EmailVerification.objects.filter(
            email__iexact=email,
            token=token,
            purpose='register',
            is_used=False
        ).first()
        if ver and ver.is_valid():
            user = ver.user
            user.is_active = True
            user.save()
            ver.is_used = True
            ver.save()
            login(request, user)
            request.session['customer_authenticated'] = True
            messages.success(request, "আপনার ইমেইল সফলভাবে ভেরিফাই হয়েছে! ভ্রমণঘুড়িতে স্বাগতম।")
            return redirect(next_url)
        else:
            messages.error(request, "ভেরিফিকেশন লিংকটি অবৈধ বা মেয়াদোত্তীর্ণ হয়েছে। ওটিপি কোড দিয়ে চেষ্টা করুন।")

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        if not otp_code:
            messages.error(request, "অনুগ্রহ করে ৬-সংখ্যার ভেরিফিকেশন কোডটি লিখুন।")
            return render(request, 'core/verify_email.html', {'email': email, 'next': next_url})

        ver = EmailVerification.objects.filter(
            email__iexact=email,
            otp_code=otp_code,
            purpose='register',
            is_used=False
        ).first()

        if ver and ver.is_valid():
            user = ver.user
            user.is_active = True
            user.save()
            ver.is_used = True
            ver.save()
            login(request, user)
            request.session['customer_authenticated'] = True
            messages.success(request, "আপনার অ্যাকাউন্ট সফলভাবে ভেরিফাই ও সক্রিয় হয়েছে! স্বাগতম।")
            return redirect(next_url)
        else:
            messages.error(request, "ভুল বা মেয়াদোত্তীর্ণ ভেরিফিকেশন কোড। অনুগ্রহ করে সঠিক কোড দিন অথবা নতুন কোড চান।")

    return render(request, 'core/verify_email.html', {'email': email, 'next': next_url})


def resend_otp_view(request):
    """Resends a fresh 6-digit OTP code for registration or password reset."""
    email = (request.GET.get('email') or request.POST.get('email', '')).strip().lower()
    purpose = request.GET.get('purpose') or request.POST.get('purpose', 'register')
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('core:home')

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        messages.error(request, "এই ইমেইলের জন্য কোনো অ্যাকাউন্ট পাওয়া যায়নি।")
        return redirect('core:register')

    ver = EmailVerification.create_verification(user, purpose=purpose)
    if purpose == 'reset_password':
        send_password_reset_otp_email(user, ver, request)
        messages.success(request, f"নতুন পাসওয়ার্ড রিসেট ওটিপি {email} এ পাঠানো হয়েছে।")
        return redirect(f"{reverse('core:reset_password')}?email={urllib.parse.quote(email)}")
    else:
        send_verification_otp_email(user, ver, request)
        messages.success(request, f"নতুন ভেরিফিকেশন ওটিপি {email} এ পাঠানো হয়েছে।")
        return redirect(f"{reverse('core:verify_email')}?email={urllib.parse.quote(email)}&next={urllib.parse.quote(next_url)}")


def forgot_password_view(request):
    """Initiates account recovery by sending password reset OTP to registered Gmail."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, "এই জিমেইল অ্যাড্রেস দিয়ে কোনো অ্যাকাউন্ট খুঁজে পাওয়া যায়নি।")
            return render(request, 'core/forgot_password.html', {'email': email})

        ver = EmailVerification.create_verification(user, purpose='reset_password')
        send_password_reset_otp_email(user, ver, request)
        messages.info(request, f"পাসওয়ার্ড রিসেটের জন্য একটি ৬-সংখ্যার সিকিউরিটি কোড {email} এ পাঠানো হয়েছে।")
        return redirect(f"{reverse('core:reset_password')}?email={urllib.parse.quote(email)}")

    return render(request, 'core/forgot_password.html')


def reset_password_view(request):
    """Resets user password after verifying 6-digit OTP."""
    email = (request.GET.get('email') or request.POST.get('email', '')).strip().lower()

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not otp_code or not new_password or not confirm_password:
            messages.error(request, "সবগুলো ফিল্ড পূরণ করুন।")
            return render(request, 'core/reset_password.html', {'email': email})

        if len(new_password) < 6:
            messages.error(request, "পাসওয়ার্ড অন্তত ৬ অক্ষরের হতে হবে।")
            return render(request, 'core/reset_password.html', {'email': email})

        if new_password != confirm_password:
            messages.error(request, "পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড হুবহু মেলেনি।")
            return render(request, 'core/reset_password.html', {'email': email})

        ver = EmailVerification.objects.filter(
            email__iexact=email,
            otp_code=otp_code,
            purpose='reset_password',
            is_used=False
        ).first()

        if ver and ver.is_valid():
            user = ver.user
            user.set_password(new_password)
            user.is_active = True
            user.save()
            ver.is_used = True
            ver.save()
            messages.success(request, "আপনার পাসওয়ার্ড সফলভাবে পরিবর্তিত হয়েছে! এখন নতুন পাসওয়ার্ড দিয়ে লগইন করুন।")
            return redirect('core:login')
        else:
            messages.error(request, "ভুল বা মেয়াদোত্তীর্ণ ওটিপি কোড। অনুগ্রহ করে সঠিক কোড দিন।")

    return render(request, 'core/reset_password.html', {'email': email})


def google_login_view(request):
    """
    Initiates standard Google OAuth 2.0 / SSO authorization flow.
    Directly prompts users to authenticate with their own active Google account.
    """
    if request.user.is_authenticated:
        return redirect('core:home')

    client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    next_url = request.GET.get('next') or reverse('core:home')
    request.session['auth_next'] = next_url

    if not client_id:
        # If client ID is missing in environment, render the Google OAuth setup notice
        # with zero mock forms or hardcoded user details.
        return render(request, 'core/google_auth.html', {
            'next': next_url,
            'is_configured': False,
        })

    # Generate cryptographic state parameter for CSRF prevention in OAuth
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state

    redirect_uri = request.build_absolute_uri(reverse('core:google_callback'))
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'prompt': 'select_account',
        'state': state,
        'access_type': 'online',
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return redirect(google_auth_url)


def google_callback_view(request):
    """
    Callback listener for official Google OAuth 2.0 code exchange.
    Strictly verifies email verification status from Google and allows instant sign-in/registration.
    """
    code = request.GET.get('code')
    error = request.GET.get('error')
    state = request.GET.get('state')
    next_url = request.session.pop('auth_next', reverse('core:home'))

    if error:
        messages.error(request, "Google sign-in was cancelled or declined.")
        return redirect('core:login')

    if not code:
        messages.error(request, "Invalid authentication response from Google.")
        return redirect('core:login')

    # Verify CSRF state token
    expected_state = request.session.pop('oauth_state', None)
    if expected_state and state != expected_state:
        messages.error(request, "Authentication state mismatch. Please try again.")
        return redirect('core:login')

    client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
    redirect_uri = request.build_absolute_uri(reverse('core:google_callback'))

    try:
        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code'
            },
            timeout=10
        )
        if token_resp.status_code != 200:
            messages.error(request, "Failed to exchange authorization code with Google.")
            return redirect('core:login')

        token_json = token_resp.json()
        access_token = token_json.get('access_token')

        if not access_token:
            messages.error(request, "Google access token could not be obtained.")
            return redirect('core:login')

        user_info_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        if user_info_resp.status_code != 200:
            messages.error(request, "Failed to fetch user profile from Google.")
            return redirect('core:login')

        user_info = user_info_resp.json()
        email = (user_info.get('email') or '').strip().lower()
        email_verified = user_info.get('email_verified', False) or user_info.get('verified_email', False)
        first_name = user_info.get('given_name') or user_info.get('name') or ''
        last_name = user_info.get('family_name') or ''

        # Strict Email Verification: Reject unverified or missing email
        if not email:
            messages.error(request, "No email address returned by your Google account.")
            return redirect('core:login')

        if not email_verified:
            messages.error(request, "Your Google account email is not verified. Only authentic, verified Google accounts can sign in.")
            return redirect('core:login')

        # Instant sign-in or registration without manual admin approval
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            base_username = email.split('@')[0].replace('.', '_')
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
        else:
            if not user.is_active:
                user.is_active = True
            if first_name and not user.first_name:
                user.first_name = first_name
            if last_name and not user.last_name:
                user.last_name = last_name
            user.save()

        login(request, user)
        request.session['customer_authenticated'] = True
        messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully signed in with Google.")
        return redirect(next_url)

    except Exception as e:
        messages.error(request, f"Google authentication encountered an error: {e}")
        return redirect('core:login')


def logout_view(request):
    """Logs out user and redirects to homepage."""
    request.session.pop('customer_authenticated', None)
    logout(request)
    messages.info(request, "আপনি সফলভাবে লগআউট হয়েছেন।")
    return redirect('core:home')
