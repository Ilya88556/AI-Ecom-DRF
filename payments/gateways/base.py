from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class PaymentGateway(ABC):
    """
    Abstract class for payment gateways
    """

    @abstractmethod
    def create_payment(
        self, order_id: int, amount: Decimal, currency: str = "UAH"
    ) -> dict[str, Any]:
        """
        Payment initialization
        """
        raise NotImplementedError

    @abstractmethod
    def check_payment_status(self, payment_token: str) -> dict[str, Any]:
        """
        Payment status checking
        """
        raise NotImplementedError
