from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_vital, name='log-vital'),
    path('my/', views.my_vitals, name='my-vitals'),
    path('patient/<int:patient_id>/', views.patient_vitals, name='patient-vitals'),
]