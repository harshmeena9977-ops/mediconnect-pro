from rest_framework import serializers
from .models import Payment


class PaymentCreateSerializer(serializers.Serializer):
    """
    Payment order banane ke liye
    Sirf appointment_id chahiye
    """
    appointment_id = serializers.IntegerField()


class PaymentVerifySerializer(serializers.Serializer):
    """
    Payment verify karne ke liye
    Razorpay se yeh teen cheezein aati hain
    """
    razorpay_order_id = serializers.CharField()
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()


class PaymentSerializer(serializers.ModelSerializer):
    """
    Payment details dikhane ke liye
    """
    patient_name = serializers.CharField(
        source='patient.full_name',
        read_only=True
    )
    appointment_date = serializers.DateField(
        source='appointment.slot.date',
        read_only=True
    )
    doctor_name = serializers.CharField(
        source='appointment.doctor.user.full_name',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'patient_name',
            'doctor_name',
            'appointment_date',
            'razorpay_order_id',
            'razorpay_payment_id',
            'amount',
            'currency',
            'status',
            'created_at'
        ]
        read_only_fields = fields