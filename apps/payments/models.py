from django.db import models
from apps.bookings.models import Booking

class Payment(models.Model):
    METHOD_CHOICES = [
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('ROCKET', 'Rocket'),
        ('CARD', 'Credit / Debit Card'),
        ('BANK', 'Bank Transfer'),
        ('CASH', 'Cash on Office'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=80, unique=True)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='BKASH')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    gateway_response = models.TextField(blank=True, help_text="JSON raw response or transaction notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.transaction_id} — {self.payment_method} (৳{self.amount:,.0f}) [{self.status}]"
