from orders.models import Order

from ..models import CarrierChoices, City, Delivery, DeliveryAddress
from .base import BaseDeliveryGateway


class PickUpGateway(BaseDeliveryGateway):
    """
    Gateway for handling self-pickup logic.
    """

    def fetch_offices(self, city: City) -> list[DeliveryAddress]:
        """
        Retrieve all active pickup delivery addresses for the specified city.
        """
        addresses = DeliveryAddress.objects.select_related("city").filter(
            carrier=CarrierChoices.PICKUP, city=city
        )
        return list(addresses)

    def create_shipment(self, order: Order, address: DeliveryAddress) -> Delivery:
        """
        Creates a delivery instance associated with the given order and delivery address.
        """
        delivery = Delivery.objects.create(
            order=order, delivery_address=address, tracking_number=""
        )

        return delivery
