from django import template
from django.db.models import Sum
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.stories.models import Story

register = template.Library()

@register.simple_tag
def get_pending_bookings():
    return Booking.objects.filter(
        status__in=['PENDING', 'PENDING_VERIFICATION']
    ).select_related('tour', 'tour_date').prefetch_related('payments').order_by('-created_at')

@register.simple_tag
def get_recent_confirmed_bookings(limit=6):
    return Booking.objects.filter(
        status='CONFIRMED'
    ).select_related('tour', 'tour_date').prefetch_related('payments').order_by('-updated_at')[:limit]

@register.simple_tag
def get_booking_stats():
    total = Booking.objects.count()
    pending = Booking.objects.filter(status__in=['PENDING', 'PENDING_VERIFICATION']).count()
    confirmed = Booking.objects.filter(status='CONFIRMED').count()
    revenue = Booking.objects.filter(status='CONFIRMED').aggregate(total=Sum('total_amount'))['total'] or 0
    stories_pending = Story.objects.filter(status=Story.STATUS_PENDING).count()
    return {
        'total': total,
        'pending': pending,
        'confirmed': confirmed,
        'revenue': revenue,
        'stories_pending': stories_pending,
    }
