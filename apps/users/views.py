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
    Naya user register karo
    Patient ya Doctor ban sakte hain
    """
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # JWT token generate karo registered user ke liye
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': f'Welcome {user.full_name}! Account successfully bana!',
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
    Email + Password se login karo
    JWT access + refresh token milega
    """
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # User authenticate karo
        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({
                'error': 'Email ya Password galat hai!'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'error': 'Account inactive hai. Support se contact karo.'
            }, status=status.HTTP_403_FORBIDDEN)

        # JWT tokens generate karo
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
    Refresh token blacklist karo — logout
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            'message': 'Successfully logout ho gaye!'
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            'error': 'Invalid token!'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Apna profile dekho — sirf logged in user
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctors_list_view(request):
    """
    Saare available doctors ki list
    Filter by: specialty, location
    """
    doctors = DoctorProfile.objects.filter(
        is_available=True
    ).select_related('user')

    # Filter by specialty
    specialty = request.query_params.get('specialty')
    if specialty:
        doctors = doctors.filter(specialty__icontains=specialty)

    # Filter by location
    location = request.query_params.get('location')
    if location:
        doctors = doctors.filter(location__icontains=location)

    serializer = DoctorProfileSerializer(doctors, many=True)
    return Response({
        'count': doctors.count(),
        'doctors': serializer.data
    }, status=status.HTTP_200_OK)
