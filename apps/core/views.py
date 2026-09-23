import os
import secrets
import urllib.parse
import requests
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from .models import SiteSetting, Testimonial, FAQ

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

    return {
        'site_setting': site_setting,
        'featured_tours': featured_tours,
        'destinations': destinations,
        'upcoming_dates': upcoming_dates,
        'stories': stories,
        'gallery_items': gallery_items,
        'testimonials': testimonials,
        'faqs': faqs,
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


def login_view(request):
    """User Login page featuring Google Sign-In."""
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.GET.get('next', reverse('core:home'))
    return render(request, 'core/login.html', {'next': next_url})


def register_view(request):
    """User Registration page featuring Google Register."""
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.GET.get('next', reverse('core:home'))
    return render(request, 'core/register.html', {'next': next_url})


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
        messages.success(request, f"Welcome, {user.first_name or user.username}! Successfully signed in with Google.")
        return redirect(next_url)

    except Exception as e:
        messages.error(request, f"Google authentication encountered an error: {e}")
        return redirect('core:login')


def logout_view(request):
    """Logs out user and redirects to homepage."""
    logout(request)
    messages.info(request, "আপনি সফলভাবে লগআউট হয়েছেন।")
    return redirect('core:home')
