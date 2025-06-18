from django.contrib import admin

from .models import Area, City, Delivery, DeliveryAddress


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the Area model.

    - Displays name, active status, Nova Poshta reference, and timestamps in the list view.
    - Allows inline editing of the 'is_active' field.
    - Enables search by area name.

    This configuration helps manage area records imported from Nova Poshta in a user-friendly way.
    """
    list_display = (
        "name",
        "is_active",
        "nova_poshta_ref",
        "time_created",
        "time_updated",
    )
    list_editable = ("is_active",)
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the City model.

    - Displays name, area, settlement type, active status, Nova Poshta reference, and timestamps in the list view.
    - Enables inline editing of the 'is_active' field.
    - Adds filters by area and settlement type.
    - Allows searching by city name.

    This admin setup facilitates efficient management of city records synchronized from Nova Poshta.
    """
    list_display = (
        "name",
        "area",
        "settlement_type_ua",
        "is_active",
        "nova_poshta_ref",
        "time_created",
        "time_updated",
    )

    search_fields = ("name",)
    list_editable = ("is_active",)
    list_filter = ("area", "settlement_type_ua")


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the DeliveryAddress model.

    - Displays carrier, address line, city, phone, office number, and active status in the list view.
    - Enables search by address line and phone number.
    - Uses autocomplete for the city field to optimize performance with large datasets.
    - Adds a filter by carrier type.

    This setup streamlines the management of delivery points (warehouses) linked to Nova Poshta.
    """
    list_display = (
        "carrier",
        "address_line",
        "city",
        "phone",
        "office_number",
        "is_active",
    )
    search_fields = ("address_line", "phone")
    autocomplete_fields = ("city",)
    list_filter = ("carrier",)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the Delivery model.

    - Displays order ID, related order object, order number, user, delivery address, tracking number, delivery costs, and creation time.
    - Adds search across order, tracking number, and user's name via related fields.
    - Provides filters by delivery carrier and creation timestamp.
    - Uses `raw_id_fields` and `autocomplete_fields` for better performance and usability on foreign key fields.
    - Includes custom methods to display order number and user in the list view.

    This setup simplifies management of delivery records and improves navigation through related objects.
    """
    list_display = (
        "order__id",
        "order",
        "order_number",
        "order_user",
        "delivery_address",
        "tracking_number",
        "delivery_costs",
        "time_created",
    )
    search_fields = ("order", "order__id", "tracking_number", "order__user__name")
    list_filter = ("delivery_address__carrier", "time_created")
    raw_id_fields = (
        "order",
        "delivery_address",
    )
    autocomplete_fields = ("delivery_address", "order")

    def order_number(self, obj):
        """
        Returns the ID of the related order for display in the admin list view.
        """
        return obj.order.id

    order_number.short_description = "Order Number"

    def order_user(self, obj):
        """
        Returns the user of related order for display in the admin list view.
        """
        return obj.order.user

    order_user.short_description = "Order User"
