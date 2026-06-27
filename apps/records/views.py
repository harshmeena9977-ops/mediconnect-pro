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
    Patient apna medical record upload karta hai
    Prescription, Lab Report, X-Ray etc.
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Sirf Patient record upload kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    serializer = MedicalRecordCreateSerializer(data=request.data)

    if serializer.is_valid():
        record = serializer.save(patient=request.user)
        return Response({
            'message': 'Medical record successfully upload ho gaya!',
            'record': MedicalRecordSerializer(record).data
        }, status=status.HTTP_201_CREATED)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_records(request):
    """
    Patient apne saare medical records dekh sakta hai
    Filter by record_type bhi kar sakte hain
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Sirf Patient apne records dekh sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    records = MedicalRecord.objects.filter(
        patient=request.user
    ).select_related('doctor', 'appointment')

    # Filter by record type
    record_type = request.query_params.get('type')
    if record_type:
        records = records.filter(
            record_type=record_type.upper()
        )

    serializer = MedicalRecordSerializer(records, many=True)
    return Response({
        'count': records.count(),
        'records': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patient_records(request, patient_id):
    """
    Doctor kisi patient ke records dekh sakta hai
    Sirf woh doctor dekh sakta hai jisne us patient ko treat kiya ho
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Sirf Doctor patient records dekh sakta hai!'
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
    Doctor medical record mein notes add karta hai
    """
    if request.user.role != 'DOCTOR':
        return Response({
            'error': 'Sirf Doctor notes add kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        record = MedicalRecord.objects.get(id=record_id)
    except MedicalRecord.DoesNotExist:
        return Response({
            'error': 'Record nahi mila!'
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorNotesSerializer(
        record,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save(doctor=request.user)
        return Response({
            'message': 'Doctor notes successfully add ho gaye!',
            'record': MedicalRecordSerializer(record).data
        }, status=status.HTTP_200_OK)

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_record(request, record_id):
    """
    Patient apna record delete kar sakta hai
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Sirf Patient apna record delete kar sakta hai!'
        }, status=status.HTTP_403_FORBIDDEN)

    try:
        record = MedicalRecord.objects.get(
            id=record_id,
            patient=request.user
        )
    except MedicalRecord.DoesNotExist:
        return Response({
            'error': 'Record nahi mila!'
        }, status=status.HTTP_404_NOT_FOUND)

    record.delete()
    return Response({
        'message': 'Record successfully delete ho gaya!'
    }, status=status.HTTP_200_OK)