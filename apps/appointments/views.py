from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from .models import AvailabilitySlot, Appointment
from .serializers import AvailabilitySlotSerializer, AppointmentSerializer


def is_doctor(user):
    """Returns True if the user has the DOCTOR role."""
    return user.role == 'DOCTOR'


def is_patient(user):
    """Returns True if the user has the PATIENT role."""
    return user.role == 'PATIENT'


# ==================== DOCTOR VIEWS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_slot(request):
    """
    Allows a Doctor to create an availability slot.
    Only users with the DOCTOR role can access this endpoint.
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Only Doctors can create slots!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        doctor_profile = request.user.doctor_profile
    except Exception:
        return Response({
            'error': 'Doctor profile not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = AvailabilitySlotSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(doctor=doctor_profile)
        return Response({
            'message': 'Slot created successfully!',
            'slot': serializer.data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_slots(request):
    """
    Returns all slots created by the authenticated Doctor.
    Supports filtering by date and booking status.
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Only Doctors can view their slots!'
        }, status=status.HTTP_403_FORBIDDEN)

    slots = AvailabilitySlot.objects.filter(
        doctor=request.user.doctor_profile
    )

    date = request.query_params.get('date')
    if date:
        slots = slots.filter(date=date)

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
    Returns all appointments for the authenticated Doctor.
    Supports filtering by appointment status.
    """
    if not is_doctor(request.user):
        return Response({
            'error': 'Only Doctors can view their appointments!'
        }, status=status.HTTP_403_FORBIDDEN)

    appointments = Appointment.objects.filter(
        doctor=request.user.doctor_profile
    ).select_related('patient', 'slot')

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
    Returns all available (unbooked) future slots.
    Supports filtering by doctor ID.
    """
    slots = AvailabilitySlot.objects.filter(
        is_booked=False,
        date__gte=timezone.now().date()
    ).select_related('doctor__user')

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
    Allows a Patient to book an available slot.
    Uses select_for_update() inside a transaction to prevent race conditions.
    """
    if not is_patient(request.user):
        return Response({
            'error': 'Only Patients can book appointments!'
        }, status=status.HTTP_403_FORBIDDEN)

    slot_id = request.data.get('slot')

    if not slot_id:
        return Response({
            'error': 'Slot ID is required!'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            # Lock the slot to prevent concurrent bookings
            slot = AvailabilitySlot.objects.select_for_update().get(
                id=slot_id
            )

            if slot.is_booked:
                return Response({
                    'error': 'This slot is already booked!'
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = AppointmentSerializer(
                data=request.data,
                context={'request': request}
            )

            if serializer.is_valid():
                appointment = serializer.save()
                return Response({
                    'message': 'Appointment booked successfully!',
                    'appointment': AppointmentSerializer(
                        appointment,
                        context={'request': request}
                    ).data
                }, status=status.HTTP_201_CREATED)

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    except AvailabilitySlot.DoesNotExist:
        return Response({
            'error': 'Slot not found!'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    """
    Returns all appointments for the authenticated Patient.
    """
    if not is_patient(request.user):
        return Response({
            'error': 'Only Patients can view their appointments!'
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
    Allows a Patient or Doctor to cancel an appointment.
    Frees up the associated slot upon cancellation.
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
            'error': 'Appointment not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    if appointment.status in ['CANCELLED', 'COMPLETED']:
        return Response({
            'error': f'Appointment is already {appointment.status}!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Cancel appointment and free the slot
    appointment.status = 'CANCELLED'
    appointment.save()

    appointment.slot.is_booked = False
    appointment.slot.save()

    return Response({
        'message': 'Appointment cancelled successfully! Slot is now available.'
    }, status=status.HTTP_200_OK)