from django.db import models
from apps.users.models import User


class HealthVital(models.Model):
    """
    IoT device se aaya health data
    BP machine, glucose meter, smartwatch — sab ka data yahan store hoga
    """
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vitals'
    )
    device_id = models.CharField(max_length=100)

    # Health Readings
    blood_pressure_sys = models.IntegerField(null=True, blank=True)  # Systolic
    blood_pressure_dia = models.IntegerField(null=True, blank=True)  # Diastolic
    heart_rate = models.IntegerField(null=True, blank=True)
    glucose_level = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

    # Alert System
    alert_triggered = models.BooleanField(default=False)
    alert_message = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'health_vitals'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.patient.full_name} | {self.timestamp}"

    def check_alerts(self):
        """
        Dangerous readings pe alert trigger karo
        """
        alerts = []

        # BP check
        if self.blood_pressure_sys and self.blood_pressure_sys > 140:
            alerts.append(f"High BP alert: {self.blood_pressure_sys}/{self.blood_pressure_dia}")

        # Heart rate check
        if self.heart_rate:
            if self.heart_rate > 100:
                alerts.append(f"High heart rate: {self.heart_rate} bpm")
            elif self.heart_rate < 60:
                alerts.append(f"Low heart rate: {self.heart_rate} bpm")

        # Glucose check
        if self.glucose_level and self.glucose_level > 140:
            alerts.append(f"High glucose: {self.glucose_level} mg/dL")

        if alerts:
            self.alert_triggered = True
            self.alert_message = " | ".join(alerts)
        
        return alerts
