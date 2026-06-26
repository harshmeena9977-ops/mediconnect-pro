from django.db import models
from apps.users.models import User, DoctorProfile


class AvailabilitySlot(models.Model):
    """
    Doctor ke available time slots
    Doctor khud define karta hai kab available hai
    """
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'availability_slots'
        # Ek doctor ek din ek time pe sirf ek slot de sakta hai
        unique_together = ['doctor', 'date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Dr.{self.doctor.user.full_name} | {self.date} | {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """
    Patient ka booked appointment
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name='appointment'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} → Dr.{self.doctor.user.full_name} | {self.status}"