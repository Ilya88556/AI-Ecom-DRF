from typing import Any

from django.http import HttpRequest
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from .models import City
from .serializers import (CarrierSerializer, CitySearchSerializer,
                          CitySerializer, DeliveryAddressQuerySerializer)
from .services import build_city_options


class DeliveryViewSet(GenericViewSet):
    """
    A ViewSet providing delivery-related actions.
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="cities")
    def cities(self, request, *args, **kwargs):
        """
        GET /api/v1/delivery/cities/?q=<term>
        Searches for cities by name__istartswith=term, but only those
        with is_active=True and at least one active DeliveryAddress.
        """
        serializer = CitySearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        term = serializer.validated_data["q"]

        qs = City.objects.filter(
            is_active=True, name__istartswith=term, delivery_addresses__is_active=True
        ).order_by("name")

        data = CitySerializer(qs, many=True).data
        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="addresses")
    def addresses(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Response:
        """
        GET /api/v1/delivery/options/?city_id=<id>

        Return list of active carriers and their offices for selected city
        """

        query_serializer = DeliveryAddressQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        city_id = query_serializer.validated_data["city_id"]

        addresses = build_city_options(city_id)
        serializer = CarrierSerializer(addresses, many=True)

        return Response(serializer.data, status=HTTP_200_OK)
