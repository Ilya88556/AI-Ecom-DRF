from typing import Any, Optional

from django.contrib import admin
from rest_framework.viewsets import GenericViewSet

from .utils import render_image_preview, short_description


class IsActiveQuerysetMixin(GenericViewSet):

    def get_queryset(self):
        """
        Returns only active objects for non-staff users.
        """
        queryset = super().get_queryset()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            return queryset.filter(is_active=True)
        return queryset


class PreviewDescriptionMixin:
    """
    Mixin for providing methods for displaying a preview and a short description.
    """

    @admin.display(description="preview")
    def image_admin_preview(self, obj: Any) -> Optional[str]:
        """
        Renders a safe HTML image tag for previewing the user's uploaded image
        inside the Django admin interface.
        """
        return render_image_preview(obj)

    @admin.display(description="Description (short)")
    def short_admin_description(self, obj: Any) -> str:
        """
        Returns a shortened version of the description field for the admin list view.
        """
        return short_description(obj)
