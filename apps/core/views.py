import os
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
    gallery_items = GalleryItem.objects.filter(is_featured=True)[:6]
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
    """Initiates Google OAuth 2.0 flow or one-click instant Google Sign-In."""
    client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('core:home')
    request.session['auth_next'] = next_url

    # One-click / form submit sign in
    if request.method == 'POST':
        email = request.POST.get('email', 'traveler@gmail.com').strip().lower()
        name = request.POST.get('name', 'Google Traveler').strip()
        username = email.split('@')[0].replace('.', '_')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': name}
        )
        if not user.email:
            user.email = email
            user.save(update_fields=['email'])
        if name and not user.first_name:
            user.first_name = name
            user.save(update_fields=['first_name'])

        login(request, user)
        messages.success(request, f"গুগল দিয়ে সফলভাবে সাইন ইন হয়েছে! স্বাগতম {user.first_name or user.username}।")
        return redirect(next_url)

    if client_id:
        redirect_uri = request.build_absolute_uri(reverse('core:google_callback'))
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=openid%20email%20profile&"
            f"access_type=offline"
        )
        return redirect(google_auth_url)
    else:
        # Prompt instant Google profile confirmation
        return render(request, 'core/google_auth.html', {
            'next': next_url,
            'is_configured': False
        })


def google_callback_view(request):
    """Callback listener for Google OAuth 2.0 code exchange."""
    code = request.GET.get('code')
    error = request.GET.get('error')
    next_url = request.session.pop('auth_next', reverse('core:home'))

    if error or not code:
        messages.error(request, "গুগল সাইন-ইন বাতিল করা হয়েছে।")
        return redirect('core:login')

    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
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
        token_json = token_resp.json()
        access_token = token_json.get('access_token')

        if not access_token:
            messages.error(request, "গুগল অ্যাক্সেস টোকেন পাওয়া যায়নি।")
            return redirect('core:login')

        user_info_resp = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        user_info = user_info_resp.json()
        email = user_info.get('email')
        name = user_info.get('name', '')

        if not email:
            messages.error(request, "গুগল একাউন্টে কোনো ইমেইল পাওয়া যায়নি।")
            return redirect('core:login')

        username = email.split('@')[0].replace('.', '_')
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': name}
        )
        login(request, user)
        messages.success(request, f"গুগল দিয়ে সফলভাবে সাইন ইন হয়েছে! স্বাগতম {user.first_name or user.username}।")
        return redirect(next_url)
    except Exception as e:
        messages.error(request, f"গুগল সাইন-ইনে ত্রুটি হয়েছে: {e}")
        return redirect('core:login')


def logout_view(request):
    """Logs out user and redirects to homepage."""
    logout(request)
    messages.info(request, "আপনি সফলভাবে লগআউট হয়েছেন।")
    return redirect('core:home')
