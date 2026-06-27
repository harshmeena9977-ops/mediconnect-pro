from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, DoctorProfile
from .models import AvailabilitySlot, Appointment


class AppointmentTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Patient banao
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='Test@1234',
            first_name='Test',
            last_name='Patient',
            role='PATIENT'
        )

        # Doctor banao
        self.doctor_user = User.objects.create_user(
            email='doctor@test.com',
            password='Test@1234',
            first_name='Test',
            last_name='Doctor',
            role='DOCTOR'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialty='General Physician',
            consultation_fee=500
        )

        # Slot banao
        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor_profile,
            date='2027-01-01',
            start_time='10:00:00',
            end_time='10:30:00'
        )

        # Patient login karo
        login = self.client.post(reverse('login'), {
            'email': 'patient@test.com',
            'password': 'Test@1234'
        }, format='json')
        self.patient_token = login.data['tokens']['access']

        # Doctor login karo
        doctor_login = self.client.post(reverse('login'), {
            'email': 'doctor@test.com',
            'password': 'Test@1234'
        }, format='json')
        self.doctor_token = doctor_login.data['tokens']['access']

    def test_book_appointment_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.patient_token}'
        )
        response = self.client.post(reverse('book-appointment'), {
            'slot': self.slot.id,
            'notes': 'Test appointment'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['appointment']['status'], 'PENDING')

    def test_double_booking_prevented(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.patient_token}'
        )
        # Pehli booking
        self.client.post(reverse('book-appointment'), {
            'slot': self.slot.id,
        }, format='json')
        # Doosri booking same slot pe
        response = self.client.post(reverse('book-appointment'), {
            'slot': self.slot.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_doctor_cannot_book(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.doctor_token}'
        )
        response = self.client.post(reverse('book-appointment'), {
            'slot': self.slot.id,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_available_slots_visible(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.patient_token}'
        )
        response = self.client.get(reverse('available-slots'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_slot_marked_booked_after_booking(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.patient_token}'
        )
        self.client.post(reverse('book-appointment'), {
            'slot': self.slot.id,
        }, format='json')
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)
