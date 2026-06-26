from rest_framework import serializers
from .models import HealthVital


class HealthVitalSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(
        source='patient.full_name',
        read_only=True
    )

    class Meta:
        model = HealthVital
        fields = [
            'id',
            'patient',
            'patient_name',
            'device_id',
            'blood_pressure_sys',
            'blood_pressure_dia',
            'heart_rate',
            'glucose_level',
            'temperature',
            'alert_triggered',
            'alert_message',
            'timestamp'
        ]
        read_only_fields = [
            'patient',
            'alert_triggered',
            'alert_message',
            'timestamp'
        ]