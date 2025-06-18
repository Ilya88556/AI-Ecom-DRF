from decimal import Decimal
from typing import Optional

from django.conf import settings
from django.db import models

from store.models import Product


class Order(models.Model):
    """
    Represents a customer's order containing one or more items.
    """

    STATUS_CHOICES = [
        ("pending", "In order"),
        ("paid", "Paid"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("canceled", "Canceled"),
        ("returned", "Returned"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Returns a string representation of the Order instance.
        """
        user_display = f"{self.user}" if self.user else "No user"
        return f"Order #{self.id} - {user_display} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def get_total_price(self) -> Decimal:
        """
        Calculates the total price of all items in the order.
        Returns:
            Decimal: The total cost of all order items.
        """
        return sum(
            (item.get_total_price() for item in self.items.all()), Decimal("0.0")
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        """
        Returns a string representation of the OrderItem instance.
        """
        return f"{self.product.name} (x{self.quantity})"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def get_total_price(self) -> Decimal:
        """
        Calculates the total price of the order item.
        """
        return self.product.price * self.quantity if self.product else None
