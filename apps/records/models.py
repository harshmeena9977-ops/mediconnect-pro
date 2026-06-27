from django.db import models
from apps.users.models import User
from apps.appointments.models import Appointment


class MedicalRecord(models.Model):
    """
    Stores patient medical records including prescriptions,
    lab reports, X-rays, and scan results.
    Doctors can attach notes to records they review.
    """
    RECORD_TYPE_CHOICES = [
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_REPORT', 'Lab Report'),
        ('XRAY', 'X-Ray'),
        ('SCAN', 'Scan'),
        ('OTHER', 'Other'),
    ]

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_records'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='records'
    )

    record_type = models.CharField(
        max_length=20,
        choices=RECORD_TYPE_CHOICES,
        default='OTHER'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to='medical_records/%Y/%m/',
        null=True,
        blank=True
    )
    doctor_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} | {self.record_type} | {self.title}"