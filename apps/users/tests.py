from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, DoctorProfile


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_patient_registration_success(self):
        data = {
            'email': 'patient@test.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '9876543210',
            'role': 'PATIENT',
            'password': 'Test@1234',
            'password2': 'Test@1234'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['role'], 'PATIENT')

    def test_doctor_registration_creates_profile(self):
        data = {
            'email': 'doctor@test.com',
            'first_name': 'Test',
            'last_name': 'Doctor',
            'phone': '9111122222',
            'role': 'DOCTOR',
            'password': 'Test@1234',
            'password2': 'Test@1234'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Doctor register hone pe DoctorProfile bhi banta hai
        user = User.objects.get(email='doctor@test.com')
        self.assertTrue(DoctorProfile.objects.filter(user=user).exists())

    def test_password_mismatch(self):
        data = {
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'PATIENT',
            'password': 'Test@1234',
            'password2': 'Wrong@1234'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_registration_blocked(self):
        data = {
            'email': 'admin@test.com',
            'first_name': 'Test',
            'last_name': 'Admin',
            'role': 'ADMIN',
            'password': 'Test@1234',
            'password2': 'Test@1234'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_blocked(self):
        data = {
            'email': 'same@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'PATIENT',
            'password': 'Test@1234',
            'password2': 'Test@1234'
        }
