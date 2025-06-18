import base64
import hashlib
import json
import random
import uuid
from decimal import Decimal
from typing import Any

from django.conf import settings

from payments.gateways.base import PaymentGateway


class MonobankPayGateway(PaymentGateway):
    """
    Monobank payment gateway emulation
    """

    @staticmethod
    def _generate_signature(data: dict | str) -> str:
        """
        Emulation signature for bank
        """

        secret_key = settings.MONOBANK_SECRET_KEY
        return hashlib.sha1(f"{secret_key}{data}{secret_key}".encode()).hexdigest()

    def create_payment(
        self, order_id: int, amount: Decimal, currency: str = "UAH"
    ) -> dict[str, Any]:
        """
        Emulating payment creation
        """

        payment_token = f"MB-{uuid.uuid4()}"

        data = {
            "order_id": order_id,
            "payment_token": payment_token,
            "amount": amount,
            "currency": currency,
            "gateway": "monobank",
            "status": "pending",
        }

        data["signature"] = self._generate_signature(data)

        return data

    def check_payment_status(self, payment_token: str) -> dict[str, Any]:
        """
        Emulating payment checks
        """
        status = random.choice(["success", "failure"])

        data_payload = {
            "payment_token": payment_token,
            "gateway": "monobank",
            "status": status,
        }

        json_data = json.dumps(data_payload)
        data_base64 = base64.b64encode(json_data.encode()).decode()

        signature = self._generate_signature(data_base64)

        return {
            "data": data_base64,
            "signature": signature,
            "gateway": "monobank",
            "payment_token": payment_token,
        }
