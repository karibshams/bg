from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Tour, Destination, TourCategory

def tour_list_view(request):
    """
    Renders tour listing. If requested via HTMX, returns only the tour grid partial
    for instant asynchronous filtering and search.
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
        
    # Filter by duration
    duration = request.GET.get('duration', '').strip()
    if duration == '1-2':
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

    # HTMX Partial Swap check
    if request.headers.get('HX-Request'):
        return render(request, 'components/tour_grid.html', {
            'tours': tours,
        })

    destinations = Destination.objects.all()
    categories = TourCategory.objects.all()
    
    return render(request, 'tours/list.html', {
        'tours': tours,
        'destinations': destinations,
        'categories': categories,
        'selected_dest': dest_slug,
        'selected_cat': cat_slug,
        'selected_duration': duration,
        'selected_sort': sort,
        'query': query,
    })


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
    
    active_dates = tour.dates.filter(is_active=True)
    inclusions = tour.inclusions.filter(is_included=True)
    exclusions = tour.inclusions.filter(is_included=False)
    
    related_tours = Tour.objects.filter(
        destination=tour.destination, 
        is_published=True
    ).exclude(id=tour.id)[:3]

    return render(request, 'tours/detail.html', {
        'tour': tour,
        'active_dates': active_dates,
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
