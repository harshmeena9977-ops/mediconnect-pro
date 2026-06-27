from django.urls import path
from . import views

urlpatterns = [
    path('create-order/', views.create_payment_order, name='create-payment-order'),
    path('verify/', views.verify_payment, name='verify-payment'),
    path('history/', views.payment_history, name='payment-history'),
    path('refund/<int:payment_id>/', views.refund_payment, name='refund-payment'),
]