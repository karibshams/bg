import uuid
from django.db import models
from django.utils import timezone
from apps.tours.models import Tour, TourDate

class Booking(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_PENDING_VERIFICATION = 'PENDING_VERIFICATION'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PENDING_VERIFICATION, 'Pending Verification'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    booking_reference = models.CharField(max_length=30, unique=True, editable=False)
    tour = models.ForeignKey(Tour, on_delete=models.PROTECT, related_name='bookings')
    tour_date = models.ForeignKey(TourDate, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    customer_address = models.CharField(max_length=255, blank=True)
    
    num_travelers = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    special_requests = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True, default='', help_text="Specific reason if the booking was rejected")
    
    # Identification Document Upload (NID / Birth Certificate)
    identification_type = models.CharField(
        max_length=50,
        choices=[
            ('NID', 'National ID Card (NID)'),
            ('BIRTH_CERT', 'Birth Certificate'),
            ('PASSPORT', 'Passport / Student ID'),
        ],
        default='NID',
        blank=True,
        verbose_name="Identification Document Type"
    )
    identification_number = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name="ID / Certificate Number",
        help_text="National ID, Birth Certificate, or Passport number"
    )
    identification_document = models.FileField(
        upload_to='bookings/documents/',
        blank=True,
        null=True,
        verbose_name="NID / Birth Certificate Document",
        help_text="Uploaded copy of NID, Birth Certificate, or Passport (Image/PDF)"
    )

    # Bus Seat Selection
    selected_seats = models.CharField(max_length=150, blank=True, default='', help_text="Comma-separated chosen seat numbers (e.g. A1, A2)")
    assigned_bus = models.ForeignKey('tours.TourBus', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    seat_selected_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            year = timezone.now().year
            while True:
                rand_code = uuid.uuid4().hex[:8].upper()
                candidate = f"BG-{year}-{rand_code}"
                if not Booking.objects.filter(booking_reference=candidate).exists():
                    self.booking_reference = candidate
                    break
        if not self.total_amount and self.unit_price:
            self.total_amount = self.unit_price * self.num_travelers
        super().save(*args, **kwargs)

    def confirm_booking(self):
        """Marks booking confirmed and updates available seats on the tour batch."""
        self.status = self.STATUS_CONFIRMED
        self.save(update_fields=['status', 'updated_at'])
        if self.tour_date:
            self.tour_date.update_available_seats()

    def cancel_booking(self):
        """Marks booking cancelled and restores seats on the tour batch."""
        self.status = self.STATUS_CANCELLED
        self.save(update_fields=['status', 'updated_at'])
        if self.tour_date:
            self.tour_date.update_available_seats()

    def reject_booking(self, reason=""):
        """Marks booking rejected with specific reason and restores seats on the tour batch."""
        self.status = self.STATUS_REJECTED
        if reason:
            self.rejection_reason = reason
        self.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        if self.tour_date:
            self.tour_date.update_available_seats()

    def get_selected_seats_list(self):
        if not self.selected_seats:
            return []
        return [s.strip() for s in self.selected_seats.split(',') if s.strip()]

    def get_selected_seats_display(self):
        seats = self.get_selected_seats_list()
        if not seats:
            return "Assigned on departure"
        seats_str = ", ".join(seats)
        if self.assigned_bus:
            return f"{seats_str} ({self.assigned_bus.bus_name})"
        return seats_str

    def __str__(self):
        return f"{self.booking_reference} - {self.customer_name} ({self.tour.title})"
