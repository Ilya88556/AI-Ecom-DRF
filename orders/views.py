import logging

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.services import OrderService

from .models import Order
from .serializers import OrderSerializer

logger = logging.getLogger("project")


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet for managing user orders.

    Supports creating new orders from the cart, retrieving individual orders,
    listing all orders for the authenticated user, and partially updating (e.g. canceling) an order.

    Allowed HTTP methods: GET, POST, PATCH.
    """

    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "patch"]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of orders belonging to the currently authenticated user.
        """
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs) -> Response:
        """
        Creates a new order by checking out the user's cart.

        On success, returns serialized order data with 201 status.
        On validation error, returns a 400 response with the error message.
        """
        addr_id = request.data.get("delivery_address_id")

        if not addr_id:
            return Response(
                {"error": "delivery_address_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = OrderService.checkout_cart(request.user, addr_id)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs) -> Response:
        """
        Partially updates an order, typically to cancel it.

        Validates incoming data and attempts to cancel the order via OrderService.
        Returns updated order data with 200 status on success, or 400 on validation error.
        """
        order = self.get_object()

        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            canceled_order = OrderService.cancel_order(order)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(canceled_order)
        return Response(serializer.data, status=status.HTTP_200_OK)
