from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from orders.models import Order


class CarrierChoices(models.TextChoices):
    """
    Enumeration for delivery carrier choices.
    """

    PICKUP = "pickup", "Pickup"
    NOVA_POSHTA = "novaposhta", "Nova Poshta"


class Area(models.Model):
    """
    Model representing a city.
    """

    name = models.CharField(max_length=100, verbose_name="name")
    is_active = models.BooleanField(default=True)
    nova_poshta_ref = models.UUIDField(
        null=True, blank=True, unique=True, verbose_name="Nova Poshta Ref"
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Created Time", db_index=True
    )
    time_updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")

    def __str__(self) -> str:
        """
        Returns a string representation of the Area instance.
        """
        return f"{self.name}"

    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"
        ordering = ["name"]


class City(models.Model):
    """
    Model representing a city.
    """

    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="cities")
    name = models.CharField(max_length=255, verbose_name="City name", db_index=True)
    is_active = models.BooleanField(default=True)
    settlement_type_ua = models.CharField(max_length=255, verbose_name="City type")
    nova_poshta_ref = models.UUIDField(
        null=True, blank=True, unique=True, verbose_name="Nova Poshta Ref"
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Created Time", db_index=True
    )
    time_updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = [
            "name",
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the City instance.
        """
        return f"{self.name} ({self.area})"


class DeliveryAddress(models.Model):
    """
    Unified model representing a delivery address for both Pickup points, Nova Poshta offices, etc.
    """

    carrier = models.CharField(
        max_length=20, choices=CarrierChoices.choices, verbose_name="Carrier"
    )
    address_line = models.CharField(max_length=255, verbose_name="Address Line")
    description = models.CharField(max_length=255, verbose_name="Description")
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        verbose_name="City",
        related_name="delivery_addresses",
    )
    phone = models.CharField(
        max_length=13, null=True, blank=True, verbose_name="Phone Number"
    )
    office_number = models.PositiveIntegerField(verbose_name="Office number", default=0)
    is_active = models.BooleanField(default=True)
    nova_poshta_ref = models.UUIDField(
        null=True, blank=True, unique=True, verbose_name="Nova Poshta Ref"
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Created Time", db_index=True
    )
    time_updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")

    class Meta:
        verbose_name = "Delivery Address"
        verbose_name_plural = "Delivery Addresses"
        ordering = ["carrier", "city__name"]

    def __str__(self) -> str:
        """
        Returns a string representation of the DeliveryAddress instance.
        """
        return f"{self.carrier} ({self.city.name}, {self.address_line})"


class Delivery(models.Model):
    """
    Model representing a delivery record for an order.
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name="Order",
        db_index=True,
    )

    delivery_address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.CASCADE,
        related_name="deliveries",
        verbose_name="Delivery Address",
    )
    tracking_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Tracking Number"
    )
    delivery_costs = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        blank=True,
        null=True,
        verbose_name="Delivery Costs",
    )
    time_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Created Time", db_index=True
    )
    time_updated = models.DateTimeField(auto_now=True, verbose_name="Updated Time")

    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"
        ordering = [
            "-time_created",
        ]

    def __str__(self) -> str:
        """
        Returns a string representation of the Delivery instance.
        """
        return (
            f"Delivery #{self.id} for Order {self.order.id} via "
            f"{self.delivery_address.carrier}"
        )
