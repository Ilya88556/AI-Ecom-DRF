from decimal import Decimal

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    Includes total price calculation.
    """

    total_price = SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "product_name",
            "product_price",
            "quantity",
            "total_price",
        )

    def get_total_price(self, obj: OrderItem) -> Decimal:
        """
        Retrieves and returns the total price of the object as a Decimal.
        """
        return obj.get_total_price()


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.

    Includes user email, status, timestamps, related order items, and computed total price.
    Provides a read-only nested representation of order items and user email.
    """

    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)
    total_price = serializers.SerializerMethodField()
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "time_created",
            "time_updated",
            "items",
            "total_price",
        )

    def validate(self, data):
        """
        Validates that the input data is not empty.

        Raises:
            serializers.ValidationError: If the incoming data dictionary is empty.
        """
        if not data:
            raise serializers.ValidationError("Request data cannot be empty")
        return data

    def get_total_price(self, obj: Order) -> Decimal:
        """
        Returns the total price of the order as a float.
        Calls the model's get_total_price method and casts the result to Decimal.
        """
        return obj.get_total_price()
