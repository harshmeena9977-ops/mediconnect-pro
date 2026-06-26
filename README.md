# 🏥 MediConnect Pro

> Production-ready Django REST API for healthcare appointment booking with JWT authentication, role-based access control, and appointment management system.

![Django](https://img.shields.io/badge/Django-6.0-green)
![DRF](https://img.shields.io/badge/DRF-3.17-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![JWT](https://img.shields.io/badge/JWT-Auth-orange)

---

## 🏗️ Architecture

```
[Postman/Mobile App]
        ↓
[Django REST Framework APIs]
        ↓
[JWT Authentication Layer]
        ↓
[PostgreSQL Database]
```

---

## 💡 Business Value

- Patients can search doctors, book appointments, and manage their health records
- Doctors can manage availability slots and view their appointment schedule  
- Admins can oversee platform activity via Django Admin panel
- Double booking prevention at database level using OneToOneField constraints

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend Framework | Django 6.0 + Django REST Framework 3.17 |
| Authentication | JWT via djangorestframework-simplejwt |
| Database | PostgreSQL 16 |
| API Documentation | Swagger/OpenAPI via drf-spectacular |
| Deployment | Render.com |

---

## 🚀 Quick Setup

```bash
# 1. Clone karo
git clone https://github.com/harshmeena9977-ops/mediconnect-pro
cd mediconnect-pro

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Dependencies install karo
pip install -r requirements.txt

# 4. Environment variables
cp .env.example .env
# .env mein apni values daalo

# 5. Database setup
python manage.py migrate

# 6. Superuser banao
python manage.py createsuperuser

# 7. Server run karo
python manage.py runserver
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register as Patient or Doctor |
| POST | `/api/v1/auth/login/` | Login and get JWT tokens |
| POST | `/api/v1/auth/logout/` | Logout and blacklist token |
| GET | `/api/v1/auth/profile/` | View own profile |
| GET | `/api/v1/auth/doctors/` | List all available doctors |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/appointments/slots/create/` | Doctor creates availability slot |
| GET | `/api/v1/appointments/slots/my/` | Doctor views own slots |
| GET | `/api/v1/appointments/slots/available/` | Patient views available slots |
| POST | `/api/v1/appointments/book/` | Patient books appointment |
| GET | `/api/v1/appointments/my/` | Patient views own appointments |
| PUT | `/api/v1/appointments/cancel/{id}/` | Cancel appointment |

---

## 🔐 Role-Based Access

| Feature | Patient | Doctor | Admin |
|---------|---------|--------|-------|
| Register/Login | ✅ | ✅ | ✅ |
| Book Appointment | ✅ | ❌ | ❌ |
| Create Slots | ❌ | ✅ | ❌ |
| View