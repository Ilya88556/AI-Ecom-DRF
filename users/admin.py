from django.contrib import admin

from .models import AuthUser


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the AuthUser model.

    Displays user details including ID, email, phone number, names,
    creation time, and last visit in the Django admin list view.
    """

    list_display = (
        "id",
        "email",
        "phone",
        "first_name",
        "last_name",
        "time_created",
        "last_visited",
    )
    list_display_links = ("email",)
    search_fields = ("email", "phone")
    list_filter = ("is_active",)
