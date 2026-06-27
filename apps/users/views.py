from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, DoctorProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    DoctorProfileSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Registers a new user as either a Patient or Doctor.
    Returns JWT tokens on successful registration.
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': f'Welcome {user.full_name}! Account created successfully!',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticates user with email and password.
    Returns JWT access and refresh tokens on success.
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({
                'error': 'Invalid email or password!'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'Account is inactive. Please contact support.'
            }, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return Response({
            'message': f'Welcome back, {user.full_name}!',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Blacklists the refresh token to invalidate the user session.
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'message': 'Successfully logged out!'
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'error': 'Invalid token!'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Returns the authenticated user's profile data.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctors_list_view(request):
    """
    Returns a list of all available doctors.
    Supports filtering by specialty and location via query parameters.
    """
    doctors = DoctorProfile.objects.filter(
        is_available=True
    ).select_related('user')

    specialty = request.query_params.get('specialty')
    if specialty:
        doctors = doctors.filter(specialty__icontains=specialty)

    location = request.query_params.get('location')
    if location:
        doctors = doctors.filter(location__icontains=location)

    serializer = DoctorProfileSerializer(doctors, many=True)
    return Response({
        'count': doctors.count(),
        'doctors': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_doctor_profile(request):
    """
    Allows a Doctor to update their profile information.
    Supports both full (PUT) and partial (PATCH) updates.
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Only Doctors can update their profile!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        doctor_profile = request.user.doctor_profile
    except DoctorProfile.DoesNotExist:
        return Response({
            'error': 'Doctor profile not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorProfileSerializer(
        doctor_profile,
        data=request.data,
        partial=request.method == 'PATCH'
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Profile updated successfully!',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, doctor_id):
    """
    Returns the full profile of a specific doctor by ID.
    """
    try:
        doctor = DoctorProfile.objects.select_related('user').get(
            id=doctor_id
        )
    except DoctorProfile.DoesNotExist:
        return Response({
            'error': 'Doctor not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorProfileSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)
