from rest_framework import serializers
from .models import MedicalRecord
from apps.users.serializers import UserProfileSerializer


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Medical record create aur view karne ke liye
    """
    patient_name = serializers.CharField(
        source='patient.full_name',
        read_only=True
    )
    doctor_name = serializers.CharField(
        source='doctor.full_name',
        read_only=True
    )

    class Meta:
        model = MedicalRecord
        fields = [
            'id',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'appointment',
            'record_type',
            'title',
            'description',
            'file',
            'doctor_notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'patient',
            'created_at',
            'updated_at'
        ]


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """
    Patient record upload karne ke liye
    """
    class Meta:
        model = MedicalRecord
        fields = [
            'appointment',
            'record_type',
            'title',
            'description',
            'file',
        ]


class DoctorNotesSerializer(serializers.ModelSerializer):
    """
    Doctor apne notes add kar sakta hai
    """
    class Meta:
        model = MedicalRecord
        fields = ['doctor_notes']