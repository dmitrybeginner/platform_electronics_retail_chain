from rest_framework.permissions import BasePermission

class IsActiveEmployee(BasePermission):
    """
    Allows access only to authenticated users that are active employees.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)
