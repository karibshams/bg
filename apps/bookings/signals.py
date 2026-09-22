from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking

@receiver(post_save, sender=Booking)
def sync_tour_date_seats_on_save(sender, instance, **kwargs):
    """Automatically recalculate seat availability whenever a booking is created or updated."""
    if instance.tour_date:
        instance.tour_date.update_available_seats()

@receiver(post_delete, sender=Booking)
def sync_tour_date_seats_on_delete(sender, instance, **kwargs):
    """Automatically restore seat availability whenever a booking is cancelled/deleted."""
    if instance.tour_date:
        instance.tour_date.update_available_seats()
