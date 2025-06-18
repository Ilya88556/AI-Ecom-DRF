from typing import Any

from django.db.models.query import QuerySet
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from cart.cart_service import (add_item_to_cart, remove_item_from_cart,
                               update_item_quantity)

from .models import Cart
from .serializers import CartItemSerializer, CartSerializer


class CartViewSet(
    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    API endpoint that allows users to interact with their shopping cart.

    Features:
    - Retrieve an authenticated user's active cart.
    - Add items to the cart.
    - Update the quantity of existing items.
    - Remove items from the cart.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def _validate_cart_item(
        self, request: Request, partial: bool = False
    ) -> dict[str, Any]:
        """
        Validate and deserialize cart item data using CartItemSerializer.
        """
        serializer = CartItemSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def _get_cart_response(self, cart: Cart) -> Response:
        """
        Serialize the given cart and return an HTTP 200 response.
        """
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def get_queryset(self) -> QuerySet[Cart]:
        """
        Get the active cart for the authenticated user.
        Returns an empty queryset if the user has no active cart.
        """
        return Cart.objects.filter(user=self.request.user, status="active")

    @action(detail=False, methods=["get"], url_path="user-cart")
    def get_user_cart(self, request: Request) -> Response:
        """
        Retrieve the authenticated user's active cart.

        Returns:
            - 200 OK: If the user has an active cart.
            - 404 Not Found: If no active cart exists.
        """

        user = request.user

        if not user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        cart = Cart.objects.active_for(user)

        if cart:
            cart = (
                Cart.objects.filter(pk=cart.pk)
                .prefetch_related("items__product")
                .first()
            )

        if not cart:
            return Response(
                {"error": "No active cart"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="add_item")
    def add_item(self, request: Request) -> Response:
        """
        Add a product to the cart or increase its quantity if it already exists.

        Request:
            - product (int): ID of the product to be added.
            - quantity (int, optional): Quantity of the product. Defaults to 1.

        Returns:
            - 200 OK: If the product is successfully added or updated.
            - 400 Bad Request: If the product is inactive.
        """
        user = request.user

        try:
            validated_data = self._validate_cart_item(request)
            product = validated_data["product"]
            quantity = validated_data.get("quantity")
            cart = add_item_to_cart(user, product, quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return self._get_cart_response(cart)

    @action(detail=False, methods=["patch"], url_path="update-item")
    def update_item(self, request: Request) -> Response:
        """
        Update the quantity of an existing product in the cart.

        Request:
            - product (int): ID of the product to update.
            - quantity (int): New quantity.

        Returns:
            - 200 OK: If the quantity is successfully updated.
            - 400 Bad Request: If the product is inactive.
            - 404 Not Found: If the cart or product is not found.
        """
        user = request.user

        try:
            validated_data = self._validate_cart_item(request, partial=True)
            product = validated_data["product"]
            quantity = validated_data.get("quantity", 1)
            cart = update_item_quantity(user, product, quantity)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        cart.refresh_from_db()

        return self._get_cart_response(cart)

    @action(detail=False, methods=["delete"], url_path="remove-item")
    def remove_item(self, request):
        """
        Remove a product from the cart.

        Request:
            - product (int): ID of the product to remove.

        Returns:
            - 200 OK: If the product was successfully removed.
            - 400 Bad Request: If no product ID is provided.
            - 404 Not Found: If the product is not found in the cart.
        """
        user = request.user

        validated_data = self._validate_cart_item(request, partial=True)
        product = validated_data["product"]
        product_id = product.id

        try:
            cart = remove_item_from_cart(user, int(product_id))
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        cart.refresh_from_db()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
