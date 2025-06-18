from __future__ import annotations

from decimal import Decimal
from typing import Optional, Tuple

from django.conf import settings
from django.db import models
from django.db.models import Q

from store.models import Product
from users.models import AuthUser


class CartQueryset(models.QuerySet):
    """
    Custom QuerySet for Cart providing additional query methods.
    """

    def active_for(self, user: AuthUser) -> Optional[Cart]:
        """
        Return the active cart for the given user, or None if no active cart exists.
        """
        return self.filter(user=user, status="active").first()


class CartManager(models.Manager):
    def get_queryset(self) -> CartQueryset:
        """
        Return a CartQueryset for the current Cart model.
        """
        return CartQueryset(self.model, using=self._db)

    def active_for(self, user: AuthUser) -> Optional[Cart]:
        """
        Return the active cart for the given user by querying the custom queryset.
        """
        return self.get_queryset().active_for(user)


class Cart(models.Model):
    """
    Represents a shopping cart associated with a user
    A cart can have one of the following statuses:
    - "active": The user is currently adding items to the cart.
    - "abandoned": The cart has been inactive for a period (not implemented yet).
    - "ordered": The cart has been converted into an order.
    """

    objects = CartManager()

    STATUS_CHOICES = [
        ("active", "Active"),
        ("abandoned", "Abandoned"),
        ("ordered", "Ordered"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

        constraints = [
            models.UniqueConstraint(
                fields=["user"], condition=Q(status="active"), name="unique_active_cart"
            ),
        ]

    def __str__(self) -> str:
        """Return a string representation of the cart."""
        return f"Cart of {self.user}"

    def get_total_price(self) -> Decimal:
        """
        Calculate the total price of all items in the cart.
        Returns:
        Decimal: The total cost of all cart items.
        """
        return sum(
            (item.get_total_price() for item in self.items.all()), Decimal("0.0")
        )

    @staticmethod
    def get_user_active_cart_or_create(user: AuthUser) -> Tuple["Cart", bool]:
        """
        Retrieves the active cart for a user or creates a new one if none exists.
        """
        return Cart.objects.get_or_create(user=user, status="active")


class CartItem(models.Model):
    """
    Represent an item in a shopping cart.
    Each item is linked to a specific product and cart
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"

    def __str__(self) -> str:
        """
        Return a string representation of the cart item.
        """
        return f"{self.product.name} (x{self.quantity})"

    def get_total_price(self) -> Decimal | None:
        """
        Calculate the total price of the cart item.
        """
        return self.product.price * self.quantity if self.product else None
