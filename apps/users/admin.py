from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DoctorProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_verified', 'created_at']
    list_filter = ['role', 'is_verified', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Role & Status', {'fields': ('role', 'is_verified', 'is_active', 'is_staff')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'experience_years', 'consultation_fee', 'rating', 'is_available']
    list_filter = ['specialty', 'is_available']
    search_fields = ['user__email', 'specialty']
