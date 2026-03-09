import os

from rest_framework.permissions import BasePermission


class IsAuthenticatedOrInternal(BasePermission):
    def has_permission(self, request, view):
        internal_token = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")
        request_token = request.headers.get("X-Internal-Token")
        if request_token and request_token == internal_token:
            return True
        return bool(request.user and request.user.is_authenticated)
