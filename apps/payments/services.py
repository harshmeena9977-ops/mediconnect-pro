import razorpay
import hmac
import hashlib
from django.conf import settings


class RazorpayService:
    """
    Razorpay ke saath saari communication yahan hoti hai
    Views mein directly Razorpay call nahi karte — service use karte hain
    Yeh pattern = Separation of Concerns
    """

    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

    def create_order(self, amount, currency='INR', notes=None):
        """
        Razorpay pe payment order banao
        Amount paise mein hoti hai — Rs 500 = 50000 paise
        """
        order_data = {
            'amount': int(amount * 100),  # Rupees to paise
            'currency': currency,
            'payment_capture': 1,  # Auto capture
            'notes': notes or {}
        }
        return self.client.order.create(data=order_data)

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Payment genuine hai ya fake — verify karo
        HMAC SHA256 signature check hota hai
        """
        try:
            # Signature verify karo
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            if generated_signature == razorpay_signature:
                return True
            return False
        except Exception:
            return False

    def refund_payment(self, razorpay_payment_id, amount=None):
        """
        Payment refund karo — cancellation pe
        Amount None hone pe full refund hota hai
        """
        refund_data = {}
        if amount:
            refund_data['amount'] = int(amount * 100)

        return self.client.payment.refund(
            razorpay_payment_id,
            refund_data
        )