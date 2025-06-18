from typing import Any

from payments.gateways.fondy import FondyPayGateway
from payments.gateways.liqpay import LiqpayPayGateway
from payments.gateways.monobank import MonobankPayGateway


class PaymentFactory:
    """
    Factory class for instantiating payment gateway handlers.
    """

    gateways = {
        "liqpay": LiqpayPayGateway,
        "fondy": FondyPayGateway,
        "monobank": MonobankPayGateway,
    }

    @staticmethod
    def get_gateway(gateway_name: str) -> Any:
        """
        Returns an instance of the payment gateway class based on the provided name.
        """
        return PaymentFactory.gateways[gateway_name.lower()]()
