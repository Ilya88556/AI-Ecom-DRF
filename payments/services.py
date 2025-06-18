import base64
import json
import logging
from decimal import Decimal
from typing import Any

from django.db import transaction

from .exceptions import PaymentGatewayException, PaymentProcessingException
from .factory import PaymentFactory
from .models import Payment

logger = logging.getLogger("project")


class PaymentService:

    @staticmethod
    def process_payment(
        order_id: int, amount: Decimal, gateway_name: str = "liqpay"
    ) -> dict[str, Any]:
        """
        Handles payment processing for a given order.

        Uses a payment gateway to initiate the payment and stores the resulting payment data in the database.
        Logs any gateway errors and raises a PaymentGatewayException on failure.
        """
        gateway = PaymentFactory.get_gateway(gateway_name)
        try:
            payment_data = gateway.create_payment(order_id, amount)
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            raise PaymentGatewayException(str(e))

        Payment.objects.create(
            order_id=order_id,
            gateway=gateway_name,
            amount=amount,
            currency=payment_data["currency"],
            payment_token=payment_data["payment_token"],
            status=payment_data["status"],
        )

        return payment_data

    @staticmethod
    @transaction.atomic
    def check_payment(
        payment_token: str, gateway_name: str = "liqpay"
    ) -> dict[str, Any]:
        """
        Verifies and updates the payment status using the provided payment token.

        Contacts the payment gateway to retrieve the current status, updates the Payment
        and associated Order records atomically, and ensures that already-processed
        payments are not reprocessed.
        """
        gateway = PaymentFactory.get_gateway(gateway_name)
        try:
            payment_data = gateway.check_payment_status(payment_token)
        except Exception as e:
            logger.error(f"Payment gateway error:  {e}")
            raise PaymentGatewayException from e

        try:
            payment = (
                Payment.objects.select_for_update()
                .select_related("order")
                .get(payment_token=payment_token)
            )
        except Payment.DoesNotExist:
            raise PaymentProcessingException("Payment not found")

        if payment.status != "pending":
            logger.info(f"Payment {payment_token}, already processed")
            return {"status": payment.status, "message": "already processed"}

        decode = base64.b64decode(payment_data["data"]).decode()
        payload = json.loads(decode)
        payment.status = payload["status"]
        payment.save()

        order = payment.order
        order.status = "paid" if payment.status == "success" else "failed"
        order.save()

        logger.info(f"Payment status updated: {payload['status']} - {payment.order}")

        return {"status": payload["status"]}
