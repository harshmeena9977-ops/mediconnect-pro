from django.db import models
from apps.users.models import User
from apps.appointments.models import Appointment


class Payment(models.Model):
    """
    Tracks payment transactions for appointments.
    Integrates with Razorpay payment gateway.
    Each appointment can have only one associated payment.
    """
    STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=200, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='CREATED'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} | ₹{self.amount} | {self.status}"