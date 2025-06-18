from decimal import Decimal

from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from store.models import Product

from .models import Cart, CartItem


class CartItemSerializer(ModelSerializer):
    """
    Serializer for CartItem model.
    Includes total price calculation.
    """

    product_id = serializers.IntegerField(write_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "product_id", "product_name", "quantity", "total_price")

    def validate(self, attrs: dict) -> dict:
        product_id = attrs.get("product_id")
        quantity = attrs.get("quantity", 1)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise NotFound({"product_id": "Product not found"})

        if not product.is_active:
            raise serializers.ValidationError(
                {"product_id": "Product is not active, you cannot buy it"}
            )

        if quantity is None or quantity < 1:
            raise serializers.ValidationError(
                {"quantity": "Quantity must be at least 1."}
            )

        attrs["product"] = product
        attrs["quantity"] = quantity

        return attrs

    def get_total_price(self, obj: CartItem) -> Decimal:
        """
        Returns the total price of the cart item.
        Relies on get_total_price(), assumes product is valid and active.
        """
        return obj.get_total_price()


class CartSerializer(ModelSerializer):
    """
    Serializer for the Cart model
    Responsible for serialization, validation, filtration
    """

    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "status",
            "items",
            "total_price",
            "time_created",
            "time_updated",
        )
        read_only_fields = ("time_created", "time_updated")

    def get_total_price(self, obj: Cart) -> Decimal:
        """
        Retrieve and return the total price of the object as a Decimal.
        """
        return obj.get_total_price()
