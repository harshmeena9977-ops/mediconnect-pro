from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import MedicalRecord
from .serializers import (
    MedicalRecordSerializer,
    MedicalRecordCreateSerializer,
    DoctorNotesSerializer
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_record(request):
    """
    Allows a Patient to upload a new medical record.
    Supports file attachments for prescriptions, reports, and scans.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only Patients can upload medical records!'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = MedicalRecordCreateSerializer(data=request.data)

    if serializer.is_valid():
        record = serializer.save(patient=request.user)
        return Response({
            'message': 'Medical record uploaded successfully!',
            'record': MedicalRecordSerializer(record).data
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_records(request):
    """
    Returns all medical records belonging to the authenticated Patient.
    Supports filtering by record type via query parameter.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only Patients can view their records!'
        }, status=status.HTTP_403_FORBIDDEN)

    records = MedicalRecord.objects.filter(
        patient=request.user
    ).select_related('doctor', 'appointment')

    record_type = request.query_params.get('type')
    if record_type:
        records = records.filter(record_type=record_type.upper())

    serializer = MedicalRecordSerializer(records, many=True)
    return Response({
        'count': records.count(),
        'records': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_records(request, patient_id):
    """
    Allows a Doctor to view a specific patient's medical records.
    Restricted to users with the DOCTOR role.
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Only Doctors can view patient records!'
        }, status=status.HTTP_403_FORBIDDEN)

    records = MedicalRecord.objects.filter(
        patient__id=patient_id
    ).select_related('doctor', 'appointment')

    serializer = MedicalRecordSerializer(records, many=True)
    return Response({
        'count': records.count(),
        'records': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def add_doctor_notes(request, record_id):
    """
    Allows a Doctor to add clinical notes to a medical record.
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Only Doctors can add notes to records!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        record = MedicalRecord.objects.get(id=record_id)
    except MedicalRecord.DoesNotExist:
        return Response({
            'error': 'Medical record not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorNotesSerializer(
        record,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save(doctor=request.user)
        return Response({
            'message': 'Doctor notes added successfully!',
            'record': MedicalRecordSerializer(record).data
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_record(request, record_id):
    """
    Allows a Patient to permanently delete one of their medical records.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only Patients can delete their records!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        record = MedicalRecord.objects.get(
            id=record_id,
            patient=request.user
        )
    except MedicalRecord.DoesNotExist:
        return Response({
            'error': 'Medical record not found!'
        }, status=status.HTTP_404_NOT_FOUND)

    record.delete()
    return Response({
        'message': 'Medical record deleted successfully!'
    }, status=status.HTTP_200_OK)