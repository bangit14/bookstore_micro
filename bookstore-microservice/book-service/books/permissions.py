from rest_framework.permissions import BasePermission


class IsManagerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {"manager", "staff"}
