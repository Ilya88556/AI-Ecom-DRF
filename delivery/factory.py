from .gateways.base import BaseDeliveryGateway
from .gateways.novaposhta import NovaPoshtaGateway
from .gateways.pickup import PickUpGateway
from .models import CarrierChoices


class DeliveryFactory:
    """
    Factory class for creating gateway instances based on carrier type.
    """

    _gateway_map = {
        CarrierChoices.PICKUP: PickUpGateway,
        CarrierChoices.NOVA_POSHTA: NovaPoshtaGateway,
    }

    @staticmethod
    def create_gateway(carrier_name: str) -> BaseDeliveryGateway:
        """
        Returns an instance of the delivery gateway class based on the provided name.
        """
        try:
            carrier_enum = CarrierChoices(carrier_name)
            return DeliveryFactory._gateway_map[carrier_enum]()
        except ValueError:
            raise ValueError(f"Unknown carrier: {carrier_name}")
