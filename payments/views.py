import base64
import json
import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from orders.models import Order

from .permissions import IsOrderOwner
from .serializers import CallbackSerializer, PaymentProcessingSerializer
from .services import PaymentService
from .utils import SignatureVerifier

logger = logging.getLogger("project")


class PaymentViewSet(GenericViewSet):
    """
    View set for creating and checking payments
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of orders with 'pending' status,
        prefetching related order items for performance optimization.
        """
        return Order.objects.filter(status="pending").prefetch_related("items")

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsOrderOwner],
    )
    def process(self, request, pk=None):
        """
        Processes payment for the specified order.

        Validates the payment gateway from request data, checks that the order total is greater than zero,
        and delegates payment processing to the PaymentService.

        Returns:
            201 with payment data on success,
            400 if validation fails or total amount is zero.
        """
        serializer = PaymentProcessingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gateway_name = serializer.validated_data["gateway"]

        order = self.get_object()

        total_amount = order.get_total_price()
        if total_amount <= 0:
            return Response(
                {"error": "Order total price must be grater then zero"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment_data = PaymentService.process_payment(
            order.id, total_amount, gateway_name
        )
        logger.info(
            f"Payment created: {payment_data['payment_token']}, Order {order.id}"
        )
        return Response(payment_data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], permission_classes=[])
    def callback(self, request):
        """
        Handles payment gateway callbacks.

        Verifies the signature of the incoming request, decodes and parses the payload,
        and checks the payment status using the payment token.

        Returns:
            403 if the signature is invalid,
            400 if the token is missing,
            200 if the payment was already processed,
            202 if the payment is still being processed.
        """
        serializer = CallbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        gateway_name = serializer.validated_data["gateway"]
        encoded_data = serializer.validated_data["data"]
        signature = serializer.validated_data["signature"]

        if not SignatureVerifier.verify_signature(
            gateway_name, encoded_data, signature
        ):
            logger.warning(f"Invalid signature")
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN
            )

        decoded_data = base64.b64decode(encoded_data).decode()
        payload = json.loads(decoded_data)

        payment_token = payload.get("payment_token")

        if not payment_token:
            return Response(
                {"error": "Missing payment token in decoded data"}, status=400
            )
        payment_status = PaymentService.check_payment(payment_token, gateway_name)

        if payment_status.get("message") == "already processed":
            return Response(payment_status, status=status.HTTP_200_OK)

        return Response(payment_status, status=status.HTTP_202_ACCEPTED)
