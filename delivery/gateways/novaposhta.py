from typing import Iterator

import requests
from django.conf import settings

from orders.models import Order

from ..models import CarrierChoices, City, Delivery, DeliveryAddress
from .base import BaseDeliveryGateway


class NovaPoshtaGateway(BaseDeliveryGateway):
    API_URL = "https://api.novaposhta.ua/v2.0/json/"

    def _post(self, model: str, method: str, properties: dict) -> list[dict]:
        """
        Sends a POST request to the Nova Poshta API with the specified model, method, and parameters,
        and returns the response data.
        """
        payload = {
            "apiKey": settings.NOVA_POSHTA_API_KEY,
            "modelName": model,
            "calledMethod": method,
            "methodProperties": properties,
        }

        response = requests.post(self.API_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])

    def get_areas(self) -> list[dict]:
        """
        Retrieves the list of all areas from the Nova Poshta API.
        """
        return self._post("AddressGeneral", "getAreas", {})

    def get_cites(self, limit=100) -> list[dict]:
        """
        Retrieves the list of all cities from the Nova Poshta API.
        """

        page = 1
        all_areas = []

        while True:
            batch = self._post(
                "AddressGeneral", "getCities", {"Limit": str(limit), "Page": str(page)}
            )

            if not batch:
                break

            all_areas.extend(batch)

            if len(batch) < limit:
                break

            page += 1

        return all_areas

    def get_warehouses(self, limit: int = 100) -> Iterator[dict]:
        """
        Retrieves the list of all addresses for city from the Nova Poshta API.
        """
        page = 1
        while True:
            batch = self._post(
                "AddressGeneral",
                "getWarehouses",
                {
                    "Limit": str(limit),
                    "Page": str(page),
                },
            )

            if not batch:
                break

            for warehouse in batch:
                yield warehouse

            if len(batch) < limit:
                break

            page += 1

    def fetch_offices(self, city: City) -> list[DeliveryAddress]:
        """
        Fetches all delivery addresses (offices) for the specified city
        associated with the Nova Poshta carrier.
        """
        addresses = DeliveryAddress.objects.select_related("city").filter(
            carrier=CarrierChoices.NOVA_POSHTA, city=city
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
