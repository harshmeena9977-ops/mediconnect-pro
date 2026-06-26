from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import HealthVital
from .serializers import HealthVitalSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_vital(request):
    """
    IoT device se health data receive karo
    Patient ka data store karo + alert check karo
    """
    serializer = HealthVitalSerializer(data=request.data)

    if serializer.is_valid():
        # Patient automatically current user
        vital = serializer.save(patient=request.user)

        # Alert check karo
        alerts = vital.check_alerts()
        vital.save()

        response_data = {
            'message': 'Health data successfully log ho gaya!',
            'vital': HealthVitalSerializer(vital).data
        }

        # Agar alert hai toh warn karo
        if alerts:
            response_data['warning'] = '⚠️ Abnormal readings detected!'
            response_data['alerts'] = alerts

        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_vitals(request):
    """
    Patient apni health history dekh sakta hai
    """
    vitals = HealthVital.objects.filter(
        patient=request.user
    )

    # Filter by alert only
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
    Doctor kisi patient ki vitals dekh sakta hai
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Sirf Doctor patient vitals dekh sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    vitals = HealthVital.objects.filter(patient__id=patient_id)

    serializer = HealthVitalSerializer(vitals, many=True)
    return Response({
        'count': vitals.count(),
        'vitals': serializer.data
    }, status=status.HTTP_200_OK)
