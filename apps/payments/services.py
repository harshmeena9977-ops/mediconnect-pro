import razorpay
import hmac
import hashlib
from django.conf import settings


class RazorpayService:
    """
    Handles all communication with the Razorpay payment gateway.
    Follows the Service Layer pattern to keep business logic
    separate from views.
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
        Creates a new payment order on Razorpay.
        Amount is converted from rupees to paise (1 INR = 100 paise).
        """
        order_data = {
            'amount': int(amount * 100),
            'currency': currency,
            'payment_capture': 1,
            'notes': notes or {}
        }
        return self.client.order.create(data=order_data)

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verifies payment authenticity using HMAC SHA256 signature.
        Prevents fraudulent payment confirmation requests.
        """
        try:
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            return generated_signature == razorpay_signature
        except Exception:
            return False

    def refund_payment(self, razorpay_payment_id, amount=None):
        """
        Initiates a refund for a successful payment.
        Passes amount in paise; if None, a full refund is issued.
        """
        refund_data = {}
        if amount:
            refund_data['amount'] = int(amount * 100)

        return self.client.payment.refund(
            razorpay_payment_id,
            refund_data
        )