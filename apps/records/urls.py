from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_record, name='upload-record'),
    path('my/', views.my_records, name='my-records'),
    path('patient/<int:patient_id>/', views.patient_records, name='patient-records'),
    path('<int:record_id>/notes/', views.add_doctor_notes, name='add-doctor-notes'),
    path('<int:record_id>/delete/', views.delete_record, name='delete-record'),
]