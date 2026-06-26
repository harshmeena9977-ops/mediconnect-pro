from django.urls import path
from . import views

urlpatterns = [
    # Doctor URLs
    path('slots/create/', views.create_slot, name='create-slot'),
    path('slots/my/', views.my_slots, name='my-slots'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor-appointments'),

    # Patient URLs
    path('slots/available/', views.available_slots, name='available-slots'),
    path('book/', views.book_appointment, name='book-appointment'),
    path('my/', views.my_appointments, name='my-appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel-appointment'),
]