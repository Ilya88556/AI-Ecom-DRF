from decimal import Decimal

from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline admin configuration for displaying Cart CartItem.
    Allows view of CartItem objects on a Cart page.
    """

    model = CartItem
    extra = 0
    fields = ("product", "quantity", "unit_price", "total_price")
    readonly_fields = ("unit_price", "total_price")

    def unit_price(self, obj: CartItem) -> Decimal | str:
        """
        Return the price of the related product if available; otherwise, return "-".
        """
        return obj.product.price if obj.product else "-"

    unit_price.short_description = "Unit Price"

    def total_price(self, obj: CartItem) -> Decimal | str:
        """
        Return the total price calculated by the object's get_total_price method.
        """
        return obj.get_total_price()

    total_price.short_description = "Total Amount"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Cart model.
    Displays key fields, and supports inline editing in the admin list view.
    """

    list_display = ("user", "status", "total_price", "time_created", "time_updated")
    list_filter = ("status",)
    search_fields = ("user__email",)
    readonly_fields = ("total_price",)

    inlines = (CartItemInline,)

    def total_price(self, obj: Decimal) -> Decimal | str:
        """
        Return the total cart price calculated by the object's get_total_price method.
        """
        return obj.get_total_price()

    total_price.short_description = "Total Cart Price"
