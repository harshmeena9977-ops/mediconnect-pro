from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta
from .models import HealthVital
from .serializers import HealthVitalSerializer, VitalsSummarySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_vital(request):
    """
    Receives health readings from an IoT device and stores them.
    Automatically checks for abnormal values and triggers alerts.
    """
    serializer = HealthVitalSerializer(data=request.data)

    if serializer.is_valid():
        vital = serializer.save(patient=request.user)

        alerts = vital.check_alerts()
        vital.save()

        response_data = {
            'message': 'Health vitals logged successfully!',
            'vital': HealthVitalSerializer(vital).data
        }

        if alerts:
            response_data['warning'] = 'Abnormal readings detected!'
            response_data['alerts'] = alerts

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_vitals(request):
    """
    Returns the authenticated patient's vital reading history.
    Supports filtering to show only alert-triggered readings.
    """
    vitals = HealthVital.objects.filter(patient=request.user)

    alerts_only = request.query_params.get('alerts_only')
    if alerts_only == 'true':
        vitals = vitals.filter(alert_triggered=True)

    serializer = HealthVitalSerializer(vitals, many=True)
    return Response({
        'count': vitals.count(),
        'vitals': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_vitals(request, patient_id):
    """
    Allows a Doctor to view a specific patient's vital history.
    Restricted to users with the DOCTOR role.
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Only Doctors can view patient vitals!'
        }, status=status.HTTP_403_FORBIDDEN)

    vitals = HealthVital.objects.filter(
        patient__id=patient_id
    )

    serializer = HealthVitalSerializer(vitals, many=True)
    return Response({
        'count': vitals.count(),
        'vitals': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def vitals_summary(request):
    """
    Returns a 7-day summary of the patient's vital readings.
    Includes averages and total alert count for trend monitoring.
    """
    seven_days_ago = timezone.now() - timedelta(days=7)

    vitals = HealthVital.objects.filter(
        patient=request.user,
        timestamp__gte=seven_days_ago
    )

    summary = vitals.aggregate(
        avg_blood_pressure_sys=Avg('blood_pressure_sys'),
        avg_heart_rate=Avg('heart_rate'),
        avg_glucose_level=Avg('glucose_level'),
    )

    response_data = {
        'avg_blood_pressure_sys': round(summary['avg_blood_pressure_sys'] or 0, 1),
        'avg_heart_rate': round(summary['avg_heart_rate'] or 0, 1),
        'avg_glucose_level': round(summary['avg_glucose_level'] or 0, 1),
        'total_readings': vitals.count(),
        'total_alerts': vitals.filter(alert_triggered=True).count(),
        'period_days': 7
    }

    return Response(response_data, status=status.HTTP_200_OK)
