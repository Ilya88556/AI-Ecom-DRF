from decimal import Decimal

from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInLine(admin.TabularInline):
    """
    Admin interface configuration for inline order items
    Displays key fields, and supports inline editing in the admin
    """

    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "unit_price", "total_price")
    readonly_fields = ("unit_price", "total_price")

    def unit_price(self, obj: OrderItem) -> Decimal | str:
        """
        Returns the price of the related product if available; otherwise, returns a dash.
        """
        return obj.product.price if obj.product else "-"

    unit_price.short_description = "Unit Price"

    def total_price(self, obj: OrderItem) -> Decimal | str:
        """
        Returns the total order item price calculated by the object's get_total_price method.
        """
        return obj.get_total_price()

    total_price.short_description = "Total Amount"


@admin.register(Order)
class OrdersAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Order model.

    Displays user, status, total price, and timestamps. Allows filtering by status,
    searching by user email, and includes inline display of related order items.
    """

    model = Order
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "time_created",
        "time_updated",
    )
    list_filter = ("status",)
    search_fields = ("user__email", "id")
    readonly_fields = ("total_price",)

    inlines = (OrderItemInLine,)

    def total_price(self, obj: Order) -> Decimal:
        """
        Returns the total order price calculated by the object's get_total_price method.
        """
        return obj.get_total_price()

    total_price.short_description = "Total Order Price"
