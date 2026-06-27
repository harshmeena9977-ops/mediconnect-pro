from rest_framework import serializers
from .models import AvailabilitySlot, Appointment
from apps.users.serializers import DoctorProfileSerializer, UserProfileSerializer


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """
    Serializes doctor availability slots for both creation and retrieval.
    Validates that end time is after start time and date is not in the past.
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
        if attrs['end_time'] <= attrs['start_time']:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time!'
            })

        from django.utils import timezone
        if attrs['date'] < timezone.now().date():
            raise serializers.ValidationError({
                'date': 'Cannot create a slot for a past date!'
            })

        return attrs


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializes appointment data including nested slot and user details.
    Automatically assigns the logged-in patient and derives doctor from slot.
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
        if slot and slot.is_booked:
            raise serializers.ValidationError({
                'slot': 'This slot is already booked!'
            })
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['patient'] = request.user

        slot = validated_data.get('slot')
        validated_data['doctor'] = slot.doctor

        appointment = Appointment.objects.create(**validated_data)

        # Mark slot as booked
        slot.is_booked = True
        slot.save()

        return appointment