from rest_framework import serializers
from .models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """
    Serializes full medical record details for retrieval.
    Includes patient and doctor names as read-only fields.
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
        read_only_fields = ['patient', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    """
    Used when a Patient uploads a new medical record.
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
    Used when a Doctor adds clinical notes to an existing record.
    """
    class Meta:
        model = MedicalRecord
        fields = ['doctor_notes']