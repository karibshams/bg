import json
from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse, Http404
from django.conf import settings
from django.db.models import Q
from .models import Tour, Destination, TourCategory, TourDate, CorporateTour
from .corporate_voucher import generate_corporate_voucher_pdf

def tour_list_view(request):
    """
    Renders tour listing with flexible travel date search, filter controls,
    and smart proximity matching for departure dates.
    If requested via HTMX, returns only the tour grid partial.
    """
    tours = Tour.objects.filter(is_published=True).select_related('destination', 'category')
    
    # Filter by search query
    query = request.GET.get('q', '').strip()
    if query:
        tours = tours.filter(
            Q(title__icontains=query) |
            Q(bangla_title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(destination__name__icontains=query) |
            Q(destination__bangla_name__icontains=query)
        )
    
    # Filter by destination
    dest_slug = request.GET.get('destination', '').strip()
    if dest_slug:
        tours = tours.filter(destination__slug=dest_slug)
        
    # Filter by category
    cat_slug = request.GET.get('category', '').strip()
    if cat_slug:
        tours = tours.filter(category__slug=cat_slug)
        
    # Filter by duration (Day Tour vs Multi-Day Tour & custom ranges)
    duration = request.GET.get('duration', '').strip()
    if duration == 'day_tour':
        tours = tours.filter(Q(duration_type='DAY_TOUR') | Q(duration_days=1))
    elif duration == 'multi_day':
        tours = tours.filter(Q(duration_type='MULTI_DAY') & Q(duration_days__gt=1))
    elif duration == '1-2':
        tours = tours.filter(duration_days__lte=2)
    elif duration == '3-4':
        tours = tours.filter(duration_days__gte=3, duration_days__lte=4)
    elif duration == '5+':
        tours = tours.filter(duration_days__gte=5)
        
    # Filter by max price
    max_price = request.GET.get('max_price', '').strip()
    if max_price and max_price.isdigit():
        tours = tours.filter(Q(discount_price__lte=int(max_price)) | Q(discount_price__isnull=True, price__lte=int(max_price)))

    # Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_asc':
        tours = tours.order_by('price')
    elif sort == 'price_desc':
        tours = tours.order_by('-price')
    elif sort == 'rating':
        tours = tours.order_by('-rating')
    else:
        tours = tours.order_by('-is_featured', '-created_at')

    # Date Search & Smart Proximity Matching
    date_str = request.GET.get('date', '').strip()
    target_date = None
    is_exact_date_match = False
    nearby_results = []

    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            target_date = None

    if target_date:
        # Check for tours departing on the exact date with available capacity
        exact_tours = tours.filter(
            dates__start_date=target_date,
            dates__is_active=True,
            dates__available_seats__gt=0
        ).distinct()

        if exact_tours.exists():
            is_exact_date_match = True
            tours = exact_tours
        else:
            # Exact date is not running! Proximity Matching:
            # Automatically display up to 5 nearby or closest available departure dates around searched date
            is_exact_date_match = False

            filtered_tour_ids = list(tours.values_list('id', flat=True))
            if filtered_tour_ids:
                nearby_dates_qs = TourDate.objects.filter(
                    tour_id__in=filtered_tour_ids,
                    is_active=True,
                    available_seats__gt=0
                ).select_related('tour', 'tour__destination', 'tour__category')
            else:
                nearby_dates_qs = TourDate.objects.none()

            # If filtered tours don't have active dates, search across all published tours
            if not nearby_dates_qs.exists():
                nearby_dates_qs = TourDate.objects.filter(
                    tour__is_published=True,
                    is_active=True,
                    available_seats__gt=0
                ).select_related('tour', 'tour__destination', 'tour__category')

            nearby_candidates = []
            seen_pairs = set()
            for td in nearby_dates_qs:
                pair_key = (td.tour_id, td.start_date)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)

                delta = (td.start_date - target_date).days
                abs_delta = abs(delta)

                if delta == 0:
                    delta_label_en = "Same Day"
                    delta_label_bn = "একই দিন"
                elif delta > 0:
                    delta_label_en = f"+{delta} day{'s' if delta > 1 else ''} later"
                    delta_label_bn = f"{delta} দিন পর"
                else:
                    delta_label_en = f"{abs(delta)} day{'s' if abs(delta) > 1 else ''} earlier"
                    delta_label_bn = f"{abs(delta)} দিন আগে"

                nearby_candidates.append({
                    'tour_date': td,
                    'tour': td.tour,
                    'delta_days': delta,
                    'abs_delta': abs_delta,
                    'delta_label_en': delta_label_en,
                    'delta_label_bn': delta_label_bn,
                })

            # Sort by closest date (smallest abs_delta), then start_date
            nearby_candidates.sort(key=lambda x: (x['abs_delta'], x['tour_date'].start_date))
            nearby_results = nearby_candidates[:5]
            # Since no exact matches exist, clear exact tours so proximity recommendations are highlighted
            tours = []

    context = {
        'tours': tours,
        'destinations': Destination.objects.all(),
        'categories': TourCategory.objects.all(),
        'selected_dest': dest_slug,
        'selected_cat': cat_slug,
        'selected_duration': duration,
        'selected_sort': sort,
        'selected_date': date_str,
        'selected_date_obj': target_date,
        'is_exact_date_match': is_exact_date_match,
        'nearby_results': nearby_results,
        'query': query,
    }

    # HTMX Partial Swap check
    if request.headers.get('HX-Request'):
        return render(request, 'components/tour_grid.html', context)

    return render(request, 'tours/list.html', context)


def tour_detail_view(request, slug):
    """
    Renders rich tour detail with dates, itineraries, gallery, inclusions,
    and sticky mobile booking CTA.
    """
    tour = get_object_or_404(
        Tour.objects.select_related('destination', 'category').prefetch_related(
            'dates', 'itineraries', 'gallery_images', 'inclusions'
        ),
        slug=slug, 
        is_published=True
    )
    
    active_dates = tour.dates.filter(is_active=True).order_by('start_date')
    selected_date_id = request.GET.get('date', '').strip()
    if selected_date_id and selected_date_id.isdigit():
        selected_date_id = int(selected_date_id)
    else:
        selected_date_id = None

    inclusions = tour.get_included_list()
    exclusions = tour.get_excluded_list()
    
    related_tours = Tour.objects.filter(
        destination=tour.destination, 
        is_published=True
    ).exclude(id=tour.id)[:3]

    return render(request, 'tours/detail.html', {
        'tour': tour,
        'active_dates': active_dates,
        'selected_date_id': selected_date_id,
        'itineraries': tour.itineraries.all(),
        'gallery_images': tour.gallery_images.all(),
        'inclusions': inclusions,
        'exclusions': exclusions,
        'related_tours': related_tours,
    })


def destination_detail_view(request, slug):
    """Renders destination detail and its matching tours."""
    destination = get_object_or_404(Destination, slug=slug)
    tours = destination.tours.filter(is_published=True)
    return render(request, 'tours/destination_detail.html', {
        'destination': destination,
        'tours': tours,
    })


def corporate_landing_view(request):
    """
    Corporate events and bespoke group tour hub.
    Allows searching proposals by reference code and showcases corporate capabilities.
    """
    query = request.GET.get('ref', '').strip().upper()
    error_message = None
    if query:
        corp = CorporateTour.objects.filter(reference_code=query, is_published=True).first()
        if corp:
            return redirect('tours:corporate_detail', reference=corp.reference_code)
        else:
            error_message = f"No corporate package found for reference code '{query}'."

    featured_tours = CorporateTour.objects.filter(is_published=True, is_featured=True)[:6]
    recent_showcase = CorporateTour.objects.filter(is_published=True)[:8]

    return render(request, 'tours/corporate_landing.html', {
        'featured_tours': featured_tours,
        'recent_showcase': recent_showcase,
        'query': query,
        'error_message': error_message,
    })


def corporate_detail_view(request, reference):
    """
    Dedicated executive frontend view for bespoke corporate packages,
    showcasing fleet allocations, group headcount, day-by-day itineraries,
    and downloadable official booking documentation.
    """
    corporate_tour = get_object_or_404(
        CorporateTour.objects.prefetch_related('destinations', 'itineraries'),
        reference_code=reference
    )
    if not corporate_tour.is_published and not request.user.is_staff:
        raise Http404("Corporate package proposal not found or unpublished.")

    itineraries = corporate_tour.itineraries.all()
    catalog_destinations = corporate_tour.destinations.all()
    
    return render(request, 'tours/corporate_detail.html', {
        'tour': corporate_tour,
        'itineraries': itineraries,
        'catalog_destinations': catalog_destinations,
    })


def corporate_voucher_view(request, reference):
    """Allows staff and corporate clients to view and download their bespoke PDF voucher."""
    corporate_tour = get_object_or_404(CorporateTour, reference_code=reference)
    pdf_bytes = generate_corporate_voucher_pdf(corporate_tour)
    filename = f"BhromonGhuri_Corporate_Voucher_{corporate_tour.reference_code}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def destination_map_api(request):
    """
    Returns JSON payload of all tourist destinations with geographic coordinates,
    cover images, and published tour packages for Leaflet.js interactive map.
    """
    destinations = Destination.objects.prefetch_related('tours').all()
    data = []
    for dest in destinations:
        lat, lng = dest.get_coordinates()
        published_tours = list(dest.tours.filter(is_published=True))
        
        tours_data = []
        for t in published_tours:
            tours_data.append({
                'id': t.id,
                'title': t.title,
                'bangla_title': t.bangla_title,
                'slug': t.slug,
                'price': float(t.price),
                'discount_price': float(t.discount_price) if t.discount_price else None,
                'duration': t.duration,
                'duration_type': getattr(t, 'duration_type', 'MULTI_DAY'),
                'duration_type_display': 'Day Tour' if getattr(t, 'duration_type', 'MULTI_DAY') == 'DAY_TOUR' else 'Multi-Day',
                'detail_url': reverse('tours:detail', args=[t.slug]),
                'image_url': t.cover_image.url if t.cover_image else (dest.cover_image.url if dest.cover_image else '/static/images/hero-sajek.jpg'),
            })

        data.append({
            'id': dest.id,
            'name': dest.name,
            'bangla_name': dest.bangla_name,
            'slug': dest.slug,
            'tagline': dest.tagline,
            'description': dest.description,
            'bangla_description': dest.bangla_description,
            'lat': lat,
            'lng': lng,
            'cover_image_url': dest.cover_image.url if dest.cover_image else '/static/images/hero-sajek.jpg',
            'detail_url': reverse('tours:destination_detail', args=[dest.slug]),
            'tours_count': len(published_tours),
            'tours': tours_data,
        })
    return JsonResponse({'destinations': data})


def bangladesh_map_view(request):
    """
    Renders interactive Bangladesh travel map powered by free and open-source
    Leaflet.js and OpenStreetMap. Allows exploring destinations and tour package previews.
    """
    destinations = Destination.objects.prefetch_related('tours').all()
    dest_list = []
    for d in destinations:
        lat, lng = d.get_coordinates()
        tours = list(d.tours.filter(is_published=True))
        dest_list.append({
            'id': d.id,
            'name': d.name,
            'bangla_name': d.bangla_name,
            'slug': d.slug,
            'tagline': d.tagline,
            'description': d.description,
            'bangla_description': d.bangla_description,
            'lat': lat,
            'lng': lng,
            'cover_image_url': d.cover_image.url if d.cover_image else '/static/images/hero-sajek.jpg',
            'detail_url': reverse('tours:destination_detail', args=[d.slug]),
            'tours_count': len(tours),
            'tours': [
                {
                    'id': t.id,
                    'title': t.title,
                    'bangla_title': t.bangla_title,
                    'slug': t.slug,
                    'price': float(t.price),
                    'discount_price': float(t.discount_price) if t.discount_price else None,
                    'duration': t.duration,
                    'duration_type': getattr(t, 'duration_type', 'MULTI_DAY'),
                    'duration_type_display': 'Day Tour' if getattr(t, 'duration_type', 'MULTI_DAY') == 'DAY_TOUR' else 'Multi-Day',
                    'detail_url': reverse('tours:detail', args=[t.slug]),
                    'image_url': t.cover_image.url if t.cover_image else (d.cover_image.url if d.cover_image else '/static/images/hero-sajek.jpg'),
                }
                for t in tours[:4]
            ]
        })

    return render(request, 'tours/map.html', {
        'destinations': destinations,
        'destinations_json': json.dumps(dest_list),
        'total_destinations': len(dest_list),
        'total_tours': sum(d['tours_count'] for d in dest_list),
        'map_api_key': getattr(settings, 'MAP_API_KEY', ''),
    })

