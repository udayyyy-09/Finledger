from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin role users can pass."""
    message = "You need admin privileges for this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin())


class IsAnalystOrAbove(BasePermission):
    """Analysts and admins can pass (viewers cannot)."""
    message = "You need analyst or admin privileges for this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_analyst())