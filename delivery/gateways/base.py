from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict

from orders.models import Order

from ..models import City, Delivery, DeliveryAddress


class BaseDeliveryGateway(ABC):
    """
    Abstract base class for delivery gateways.
    This class defines the interface for delivery gateway implementations.
    """

    @abstractmethod
    def fetch_offices(self, city: City) -> list[DeliveryAddress]:
        """
        Retrieve a list of delivery offices located in the specified city.
        """
        raise NotImplementedError

    @abstractmethod
    def create_shipment(self, order: Order, address: DeliveryAddress) -> Delivery:
        """
        Create a shipment for the given order and delivery address.

        This method is responsible for initiating the shipment process with the delivery gateway,
        using the provided order and selected delivery address.
        """
        raise NotImplementedError
