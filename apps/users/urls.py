from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Doctor URLs
    path('doctors/', views.doctors_list_view, name='doctors-list'),
    path('doctors/<int:doctor_id>/', views.doctor_detail, name='doctor-detail'),
    path('doctor/profile/update/', views.update_doctor_profile, name='doctor-profile-update'),
]