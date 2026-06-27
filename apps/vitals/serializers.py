from rest_framework import serializers
from .models import HealthVital


class HealthVitalSerializer(serializers.ModelSerializer):
    """
    Serializes health vital readings for both logging and retrieval.
    Patient is automatically assigned from the authenticated user.
    """
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


class VitalsSummarySerializer(serializers.Serializer):
    """
    Provides a summary of the last 7 days of vital readings.
    Used for trend analysis and doctor review.
    """
    avg_blood_pressure_sys = serializers.FloatField()
    avg_heart_rate = serializers.FloatField()
    avg_glucose_level = serializers.FloatField()
    total_readings = serializers.IntegerField()
    total_alerts = serializers.IntegerField()
    period_days = serializers.IntegerField()