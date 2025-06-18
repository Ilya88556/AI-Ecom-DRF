from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    """
    Custom permission to only allow staff users to edit or create objects.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated and request.user.is_staff


class ReviewPermission(BasePermission):
    """
    Permission for reviews:
    - GET: All users (but only moderated reviews, except for owners)
    - POST: Only authenticated users
    - PUT/PATCH: Owner can edit if not moderated, staff can edit anything
    - DELETE: only staff
    """

    def has_permission(self, request, view):
        """
        Allows GET for all users, Post authenticated only
        """
        if request.method == "POST":
            return request.user.is_authenticated and not request.user.is_staff
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if request.method == "DELETE":
            return request.user.is_authenticated and request.user.is_staff

        if request.method in ["PUT", "PATCH"]:
            if request.user.is_authenticated and request.user.is_staff:
                return True
            return (
                request.user.is_authenticated
                and obj.user == request.user
                and not obj.moderated
            )
        return False
