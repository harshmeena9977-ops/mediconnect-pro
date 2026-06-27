from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = [
        'patient',
        'record_type',
        'title',
        'doctor',
        'created_at'
    ]
    list_filter = ['record_type']
    search_fields = ['patient__email', 'title']