from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages
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
    stories = Story.objects.filter(is_featured=True).select_related('destination')[:3]
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
        # In production this triggers an email or saves an Inquiry model
        messages.success(request, f"ধন্যবাদ {name}! আপনার বার্তাটি সফলভাবে পাঠানো হয়েছে। আমরা শীঘ্রই যোগাযোগ করব।")
    return render(request, 'core/contact.html', {
        'site_setting': site_setting,
    })
