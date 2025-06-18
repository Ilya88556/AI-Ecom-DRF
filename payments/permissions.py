from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOrderOwner(BasePermission):
    """
    Custom permission to allow access only to the owner of the order.
    Grants permission if the user is authenticated and is the owner of the order object.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return obj.user == request.user
