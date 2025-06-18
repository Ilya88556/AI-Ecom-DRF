from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Payment model.
    """

    list_display = [
        "order",
        "gateway",
        "payment_token",
        "status",
        "amount",
        "currency",
        "time_created",
        "time_updated",
    ]

    list_filter = ("gateway", "status", "currency")
    ordering = ("-time_created",)
    search_fields = ("order__id",)
