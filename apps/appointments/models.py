from django.db import models
from apps.users.models import User, DoctorProfile


class AvailabilitySlot(models.Model):
    """
    Represents a time slot that a Doctor makes available for appointments.
    Each slot is unique per doctor, date, and start time.
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
        # Prevents a doctor from creating duplicate slots
        unique_together = ['doctor', 'date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"Dr.{self.doctor.user.full_name} | {self.date} | {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    """
    Represents a confirmed booking between a Patient and a Doctor.
    Links to a specific AvailabilitySlot using OneToOneField
    to prevent double booking at the database level.
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
    # OneToOneField ensures only one appointment per slot — database level constraint
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