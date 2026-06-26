from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import AvailabilitySlot, Appointment
from .serializers import AvailabilitySlotSerializer, AppointmentSerializer


def is_doctor(user):
    return user.role == 'DOCTOR'


def is_patient(user):
    return user.role == 'PATIENT'


# ==================== DOCTOR VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_slot(request):
    """
    Doctor apna available slot create karta hai
    Sirf DOCTOR role wala user kar sakta hai
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Sirf Doctor slot create kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    # Doctor ka profile lo
    try:
        doctor_profile = request.user.doctor_profile
    except Exception:
        return Response({
            'error': 'Doctor profile nahi mila!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = AvailabilitySlotSerializer(data=request.data)

    if serializer.is_valid():
        # Automatically doctor set hoga
        serializer.save(doctor=doctor_profile)
        return Response({
            'message': 'Slot successfully create ho gaya!',
            'slot': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_slots(request):
    """
    Doctor apne saare slots dekh sakta hai
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Sirf Doctor apne slots dekh sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    slots = AvailabilitySlot.objects.filter(
        doctor=request.user.doctor_profile
    )

    # Filter by date
    date = request.query_params.get('date')
    if date:
        slots = slots.filter(date=date)

    # Filter by booked status
    is_booked = request.query_params.get('is_booked')
    if is_booked is not None:
        slots = slots.filter(is_booked=is_booked.lower() == 'true')

    serializer = AvailabilitySlotSerializer(slots, many=True)
    return Response({
        'count': slots.count(),
        'slots': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_appointments(request):
    """
    Doctor apne saare appointments dekh sakta hai
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Sirf Doctor apne appointments dekh sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    appointments = Appointment.objects.filter(
        doctor=request.user.doctor_profile
    ).select_related('patient', 'slot')

    # Filter by status
    appt_status = request.query_params.get('status')
    if appt_status:
        appointments = appointments.filter(status=appt_status.upper())

    serializer = AppointmentSerializer(appointments, many=True)
    return Response({
        'count': appointments.count(),
        'appointments': serializer.data
    }, status=status.HTTP_200_OK)


# ==================== PATIENT VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_slots(request):
    """
    Patient kisi bhi doctor ke available slots dekh sakta hai
    ?doctor_id=1 se filter kar sakte hain
    """
    slots = AvailabilitySlot.objects.filter(
        is_booked=False,
        date__gte=timezone.now().date()  # Sirf future slots
    ).select_related('doctor__user')

    # Filter by doctor
    doctor_id = request.query_params.get('doctor_id')
    if doctor_id:
        slots = slots.filter(doctor__id=doctor_id)

    serializer = AvailabilitySlotSerializer(slots, many=True)
    return Response({
        'count': slots.count(),
        'available_slots': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    """
    Patient appointment book karta hai
    Sirf PATIENT role wala user kar sakta hai
    """
    if not is_patient(request.user):
        return Response({
            'error': 'Sirf Patient appointment book kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = AppointmentSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        appointment = serializer.save()
        return Response({
            'message': 'Appointment successfully book ho gayi!',
            'appointment': AppointmentSerializer(
                appointment,
                context={'request': request}
            ).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    """
    Patient apne saare appointments dekh sakta hai
    """
    if not is_patient(request.user):
        return Response({
            'error': 'Sirf Patient apne appointments dekh sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    appointments = Appointment.objects.filter(
        patient=request.user
    ).select_related('doctor__user', 'slot')

    serializer = AppointmentSerializer(appointments, many=True)
    return Response({
        'count': appointments.count(),
        'appointments': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, appointment_id):
    """
    Patient ya Doctor — dono appointment cancel kar sakte hain
    """
    try:
        if is_patient(request.user):
            appointment = Appointment.objects.get(
                id=appointment_id,
                patient=request.user
            )
        else:
            appointment = Appointment.objects.get(
                id=appointment_id,
                doctor=request.user.doctor_profile
            )
    except Appointment.DoesNotExist:
        return Response({
            'error': 'Appointment nahi mili!'
        }, status=status.HTTP_404_NOT_FOUND)

    # Already cancelled ya completed?
    if appointment.status in ['CANCELLED', 'COMPLETED']:
        return Response({
            'error': f'Appointment already {appointment.status} hai!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Cancel karo aur slot free karo
    appointment.status = 'CANCELLED'
    appointment.save()

    # Slot wapas available karo
    appointment.slot.is_booked = False
    appointment.slot.save()

    return Response({
        'message': 'Appointment cancel ho gayi! Slot wapas available hai.'
    }, status=status.HTTP_200_OK)