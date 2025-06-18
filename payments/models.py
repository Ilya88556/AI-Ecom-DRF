from django.db import models

from orders.models import Order


class Payment(models.Model):
    """
    Model representing a payment transaction.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("success", "Success"),
        ("failure", "Failure"),
    )

    GATEWAY_CHOICES = (
        ("liqpay", "LiqPay"),
        ("monobank", "Monobank"),
        ("fondy", "Fondy"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default="UAH")
    payment_token = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self) -> str:
        return f"{self.order.id} - {self.gateway} - {self.status}"
