from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),

    # Auth APIs
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/appointments/', include('apps.appointments.urls')),  # ← Yeh add karo
    path('api/v1/vitals/', include('apps.vitals.urls')),

    # API Documentation — Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        url_name='schema'), name='swagger-ui'),
]
