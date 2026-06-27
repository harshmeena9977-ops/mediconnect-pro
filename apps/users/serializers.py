from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, DoctorProfile


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration for both Patient and Doctor roles.
    Validates password confirmation and prevents Admin registration via API.
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
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match!'
            })

        if attrs.get('role') == 'ADMIN':
            raise serializers.ValidationError({
                'role': 'Admin accounts cannot be created via API!'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)

        # Automatically create DoctorProfile when a Doctor registers
        if user.role == 'DOCTOR':
            DoctorProfile.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates email and password credentials for JWT login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializes user profile data for read operations.
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
    Serializes doctor profile including nested user information.
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