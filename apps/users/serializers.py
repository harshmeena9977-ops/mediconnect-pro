from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, DoctorProfile


class RegisterSerializer(serializers.ModelSerializer):
    """
    Naya user register karne ke liye
    Patient ya Doctor — dono register kar sakte hain
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone',
            'role',
            'password',
            'password2'
        ]

    def validate(self, attrs):
        # Dono passwords match karte hain?
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Dono passwords alag hain!'
            })

        # Role valid hai?
        if attrs.get('role') == 'ADMIN':
            raise serializers.ValidationError({
                'role': 'Admin account API se nahi ban sakta!'
            })

        return attrs

    def create(self, validated_data):
        # password2 ki zaroorat nahi ab
        validated_data.pop('password2')

        # User banao
        user = User.objects.create_user(**validated_data)

        # Agar Doctor hai toh automatically DoctorProfile bhi banao
        if user.role == 'DOCTOR':
            DoctorProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Email + Password leke JWT token deta hai
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    User ka profile dikhane ke liye
    """
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone',
            'role',
            'is_verified',
            'created_at'
        ]
        read_only_fields = ['email', 'role', 'is_verified', 'created_at']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Doctor ka extended profile
    """
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id',
            'user',
            'specialty',
            'experience_years',
            'consultation_fee',
            'rating',
            'location',
            'bio',
            'is_available'
        ]