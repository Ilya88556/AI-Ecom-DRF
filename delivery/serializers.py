from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer

from .models import City, DeliveryAddress


class CitySearchSerializer(Serializer):
    """
    Validation of the 'q' parameter for city search (minimum 3 characters).
    """

    q = serializers.CharField(
        min_length=3,
        help_text="Minimal 3 characters for searching city",
        error_messages={
            "required": "The 'q' parameter is required.",
            "min_length": "Enter at least 3 characters.",
        },
    )


class CitySerializer(ModelSerializer):
    """
    Simple serializer for the City model.
    Used in the /cities endpoint.
    """

    class Meta:
        model = City
        fields = ["id", "name", "area"]


class DeliveryAddressQuerySerializer(Serializer):
    """
    Serializer for validating city_id from query parameters.
    Ensures the city exists and is active.
    """

    city_id = serializers.IntegerField(
        required=True,
        help_text="ID of the city",
        error_messages={
            "required": "Area ID is required",
            "invalid": "Uncorrected area ID",
        },
    )

    def validate_city_id(self, value: int) -> int:
        """
        Field-level validation for city_id.
        Checks that the city exists and is active.
        """
        try:
            return City.objects.get(id=value, is_active=True)
        except City.DoesNotExist:
            raise serializers.ValidationError(f"City with ID {value} does not exist.")


class DeliveryAddressSerializer(ModelSerializer):
    """
    Serializer for DeliveryAddress model.
    For delivery addresses from external API (Nova Poshta, etc.), instances may be unsaved.
    """

    class Meta:
        model = DeliveryAddress
        fields = ("id", "carrier", "address_line", "city", "phone", "office_number")


class CarrierSerializer(Serializer):
    """
    Serializer representing a carrier and its associated delivery addresses.

    Fields:
        - carrier (dict): A dictionary containing carrier metadata (e.g. name, ID, slug).
        - addresses (list): A list of delivery addresses serialized via DeliveryAddressSerializer.

    This serializer is useful for grouping delivery points under a single carrier,
    for example when returning structured data to the frontend.
    """

    carrier = serializers.DictField()
    addresses = DeliveryAddressSerializer(many=True)
