from django.db import models
from apps.users.models import User


class HealthVital(models.Model):
    """
    Stores health readings received from IoT devices such as
    smartwatches, BP machines, and glucose meters.
    Automatically triggers alerts when readings exceed safe thresholds.
    """
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vitals'
    )
    device_id = models.CharField(max_length=100)

    blood_pressure_sys = models.IntegerField(null=True, blank=True)
    blood_pressure_dia = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    glucose_level = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

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
        Checks all vital readings against safe thresholds.
        Sets alert_triggered to True if any reading is abnormal.
        Returns a list of alert messages.
        """
        alerts = []

        if self.blood_pressure_sys and self.blood_pressure_sys > 140:
            alerts.append(
                f"High blood pressure detected: {self.blood_pressure_sys}/{self.blood_pressure_dia} mmHg"
            )

        if self.heart_rate:
            if self.heart_rate > 100:
                alerts.append(f"Elevated heart rate: {self.heart_rate} bpm")
            elif self.heart_rate < 60:
                alerts.append(f"Low heart rate: {self.heart_rate} bpm")

        if self.glucose_level and self.glucose_level > 140:
            alerts.append(f"High glucose level: {self.glucose_level} mg/dL")

        if self.temperature and self.temperature > 99.5:
            alerts.append(f"Fever detected: {self.temperature}°F")

        if alerts:
            self.alert_triggered = True
            self.alert_message = " | ".join(alerts)

        return alerts
