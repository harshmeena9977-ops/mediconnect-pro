from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
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
    Step 1 — Razorpay order banao
    Patient appointment book karne ke baad yeh call karta hai
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Sirf Patient payment kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = PaymentCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    appointment_id = serializer.validated_data['appointment_id']

    # Appointment check karo
    try:
        appointment = Appointment.objects.get(
            id=appointment_id,
            patient=request.user,
            status='PENDING'
        )
    except Appointment.DoesNotExist:
        return Response({
            'error': 'Appointment nahi mili ya already paid hai!'
        }, status=status.HTTP_404_NOT_FOUND)

    # Already payment exist karta hai?
    if hasattr(appointment, 'payment'):
        return Response({
            'error': 'Is appointment ka payment already create ho chuka hai!'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Amount doctor ki fee se lo
    amount = appointment.doctor.consultation_fee

    try:
        # Razorpay order banao
        razorpay_service = RazorpayService()
        order = razorpay_service.create_order(
            amount=float(amount),
            notes={
                'appointment_id': str(appointment.id),
                'patient': request.user.full_name,
                'doctor': appointment.doctor.user.full_name
            }
        )

        # Payment DB mein save karo
        payment = Payment.objects.create(
            appointment=appointment,
            patient=request.user,
            razorpay_order_id=order['id'],
            amount=amount
        )

        return Response({
            'message': 'Payment order create ho gaya!',
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'payment_id': payment.id,
            'key_id': razorpay_service.client.auth[0]
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': f'Payment order create nahi hua: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Step 2 — Payment verify karo
    Razorpay frontend se yeh 3 values aati hain
    Signature check karke appointment CONFIRMED karo
    """
    serializer = PaymentVerifySerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    try:
        with transaction.atomic():
            # Payment dhundho
            payment = Payment.objects.select_for_update().get(
                razorpay_order_id=data['razorpay_order_id'],
                patient=request.user
            )

            # Signature verify karo
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

            # Payment successful — update karo
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            payment.status = 'SUCCESS'
            payment.save()

            # Appointment CONFIRMED karo
            payment.appointment.status = 'CONFIRMED'
            payment.appointment.save()

            return Response({
                'message': 'Payment successful! Appointment confirmed ho gayi!',
                'payment': PaymentSerializer(payment).data
            }, status=status.HTTP_200_OK)

    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment nahi mili!'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    """
    Patient apni payment history dekh sakta hai
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Sirf Patient payment history dekh sakta hai!'
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
    Appointment cancel hone pe refund karo
    """
    try:
        payment = Payment.objects.get(
            id=payment_id,
            patient=request.user,
            status='SUCCESS'
        )
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment nahi mili ya refund eligible nahi!'
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        razorpay_service = RazorpayService()
        razorpay_service.refund_payment(
            payment.razorpay_payment_id,
            float(payment.amount)
        )

        # Payment status update karo
        payment.status = 'REFUNDED'
        payment.save()

        # Appointment cancel karo
        payment.appointment.status = 'CANCELLED'
        payment.appointment.save()

        # Slot free karo
        payment.appointment.slot.is_booked = False
        payment.appointment.slot.save()

        return Response({
            'message': 'Refund successful! Appointment cancel ho gayi.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': f'Refund failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)