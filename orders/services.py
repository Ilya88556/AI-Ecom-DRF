import logging

from django.db import transaction
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from cart.models import Cart, CartItem
from delivery.factory import DeliveryFactory
from delivery.models import DeliveryAddress
from orders.models import Order, OrderItem
from users.models import AuthUser

logger = logging.getLogger("project")


class OrderService:
    @staticmethod
    @transaction.atomic
    def checkout_cart(user: AuthUser, delivery_address_id: int) -> Order:
        """
        Process the checkout of an active cart and create an order.
        """

        cart: Cart = (
            Cart.objects.filter(user=user, status="active")
            .prefetch_related(
                Prefetch("items", queryset=CartItem.objects.select_related("product"))
            )
            .first()
        )

        if not cart or not cart.items.exists():
            raise ValidationError("Cart is empty or doesn't exist")

        order: Order = Order.objects.create(user=user, status="pending")

        order_items: list[OrderItem] = [
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
            )
            for item in cart.items.all()
        ]

        OrderItem.objects.bulk_create(order_items)
        cart.status = "ordered"
        cart.save()

        try:
            address = DeliveryAddress.objects.get(
                id=delivery_address_id, is_active=True
            )
        except DeliveryAddress.DoesNotExist:
            raise ValidationError(
                f"DeliveryAddress with ID {delivery_address_id} not found"
            )

        gateway = DeliveryFactory.create_gateway(address.carrier)
        gateway.create_shipment(order, address)

        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order):
        """
        Cancels an order if it is not already shipped or delivered.
        """

        if order.status in ["shipped", "delivered", "canceled", "returned", "failed"]:
            raise ValidationError(
                "Cannot cancel a shipped, delivered, returned, failed or canceled order"
            )

        order.status = "canceled"
        order.save()

        return order
