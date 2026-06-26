from rest_framework import serializers
from .models import AvailabilitySlot, Appointment
from apps.users.serializers import DoctorProfileSerializer, UserProfileSerializer


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """
    Doctor ke slots — create aur view dono ke liye
    """
    doctor_name = serializers.CharField(
        source='doctor.user.full_name',
        read_only=True
    )

    class Meta:
        model = AvailabilitySlot
        fields = [
            'id',
            'doctor',
            'doctor_name',
            'date',
            'start_time',
            'end_time',
            'is_booked',
            'created_at'
        ]
        read_only_fields = ['is_booked', 'created_at']

    def validate(self, attrs):
        # End time, start time se baad honi chahiye
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({
                'end_time': 'End time, start time se baad honi chahiye!'
            })

        # Past date pe slot nahi ban sakta
        from django.utils import timezone
        if attrs['date'] < timezone.now().date():
            raise serializers.ValidationError({
                'date': 'Past date pe slot nahi ban sakta!'
            })

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Appointment book karne ke liye
    """
    patient_name = serializers.CharField(
        source='patient.full_name',
        read_only=True
    )
    doctor_name = serializers.CharField(
        source='doctor.user.full_name',
        read_only=True
    )
    slot_details = AvailabilitySlotSerializer(
        source='slot',
        read_only=True
    )

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'slot',
            'slot_details',
            'status',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'patient',
            'doctor',
            'status',
            'created_at',
            'updated_at'
        ]

    def validate(self, attrs):
        slot = attrs.get('slot')

        # Slot already booked hai?
        if slot and slot.is_booked:
            raise serializers.ValidationError({
                'slot': 'Yeh slot already booked hai!'
            })

        return attrs

    def create(self, validated_data):
        # Patient automatically current logged in user hoga
        request = self.context.get('request')
        validated_data['patient'] = request.user

        # Doctor slot se automatically set hoga
        slot = validated_data.get('slot')
        validated_data['doctor'] = slot.doctor

        # Appointment banao
        appointment = Appointment.objects.create(**validated_data)

        # Slot ko booked mark karo
        slot.is_booked = True
        slot.save()

        return appointment