import os

from rest_framework.permissions import BasePermission


class IsManagerOrStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {"manager", "staff"}


class IsManagerOrStaffOrInternal(BasePermission):
    def has_permission(self, request, view):
        internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")
        request_token = request.headers.get("X-Internal-Token")
        if request_token and request_token == internal_token:
            return True

        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {"manager", "staff"}


class IsManagerStaffOrCustomer(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {"manager", "staff", "customer"}
