from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'patient',
        'amount',
        'status',
        'razorpay_order_id',
        'created_at'
    ]
    list_filter = ['status', 'currency']
    search_fields = ['patient__email', 'razorpay_order_id']
    readonly_fields = [
        'razorpay_order_id',
        'razorpay_payment_id',
        'razorpay_signature',
        'created_at',
        'updated_at'
    ]