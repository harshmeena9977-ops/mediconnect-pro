from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from apps.appointments.models import Appointment
from .models import Payment
from .serializers import (
    PaymentCreateSerializer,
    PaymentVerifySerializer,
    PaymentSerializer
)
from .services import RazorpayService


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_order(request):
    """
    Creates a Razorpay order for a pending appointment.
    Called by the Patient after booking an appointment.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only Patients can initiate payments!'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = PaymentCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    appointment_id = serializer.validated_data['appointment_id']

    try:
        appointment = Appointment.objects.get(
            id=appointment_id,
            patient=request.user,
            status='PENDING'
        )
    except Appointment.DoesNotExist:
        return Response({
            'error': 'Appointment not found or already paid!'
        }, status=status.HTTP_404_NOT_FOUND)

    if hasattr(appointment, 'payment'):
        return Response({
            'error': 'A payment order already exists for this appointment!'
        }, status=status.HTTP_400_BAD_REQUEST)

    amount = appointment.doctor.consultation_fee

    try:
        razorpay_service = RazorpayService()
        order = razorpay_service.create_order(
            amount=float(amount),
            notes={
                'appointment_id': str(appointment.id),
                'patient': request.user.full_name,
                'doctor': appointment.doctor.user.full_name
            }
        )

        payment = Payment.objects.create(
            appointment=appointment,
            patient=request.user,
            razorpay_order_id=order['id'],
            amount=amount
        )

        return Response({
            'message': 'Payment order created successfully!',
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'payment_id': payment.id,
            'key_id': razorpay_service.client.auth[0]
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Failed to create payment order: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verifies the Razorpay payment signature and confirms the appointment.
    Uses select_for_update() to prevent concurrent verification issues.
    """
    serializer = PaymentVerifySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data

    try:
        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(
                razorpay_order_id=data['razorpay_order_id'],
                patient=request.user
            )

            razorpay_service = RazorpayService()
            is_valid = razorpay_service.verify_payment(
                data['razorpay_order_id'],
                data['razorpay_payment_id'],
                data['razorpay_signature']
            )

            if not is_valid:
                payment.status = 'FAILED'
                payment.save()
                return Response({
                    'error': 'Payment verification failed! Invalid signature.'
                }, status=status.HTTP_400_BAD_REQUEST)

            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.status = 'SUCCESS'
            payment.save()

            # Confirm the appointment after successful payment
            payment.appointment.status = 'CONFIRMED'
            payment.appointment.save()

            return Response({
                'message': 'Payment successful! Appointment confirmed.',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_200_OK)

    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment record not found!'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """
    Returns the complete payment history for the authenticated Patient.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only Patients can view payment history!'
        }, status=status.HTTP_403_FORBIDDEN)

    payments = Payment.objects.filter(
        patient=request.user
    ).select_related(
        'appointment__doctor__user',
        'appointment__slot'
    )

    serializer = PaymentSerializer(payments, many=True)
    return Response({
        'count': payments.count(),
        'payments': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refund_payment(request, payment_id):
    """
    Processes a refund for a successful payment.
    Cancels the associated appointment and frees the slot.
    """
    try:
        payment = Payment.objects.get(
            id=payment_id,
            patient=request.user,
            status='SUCCESS'
        )
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found or not eligible for refund!'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        razorpay_service = RazorpayService()
        razorpay_service.refund_payment(
            payment.razorpay_payment_id,
            float(payment.amount)
        )

        payment.status = 'REFUNDED'
        payment.save()

        payment.appointment.status = 'CANCELLED'
        payment.appointment.save()

        payment.appointment.slot.is_booked = False
        payment.appointment.slot.save()

        return Response({
            'message': 'Refund processed successfully! Appointment cancelled.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Refund failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)