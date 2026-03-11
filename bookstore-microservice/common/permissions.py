"""
Common permission decorators for role-based access control across all microservices.

Roles:
- customer: Basic customer access
- staff: Employee access with product and order management
- manager: Full administrative access
"""

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import jwt
import os


def extract_role_from_token(request):
    """Extract role from JWT token in Authorization header."""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    
    try:
        jwt_secret = os.getenv('JWT_SIGNING_KEY', 'bookstore-shared-jwt-secret')
        payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        return payload.get('role')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_role(*allowed_roles):
    """
    Decorator to restrict access to specific roles.
    
    Usage:
        @require_role('manager')
        @require_role('manager', 'staff')
        @require_role('customer', 'staff', 'manager')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            role = extract_role_from_token(request)
            
            if role is None:
                return Response(
                    {"error": "Authentication required", "detail": "Valid JWT token not provided"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            if role not in allowed_roles:
                return Response(
                    {
                        "error": "Permission denied",
                        "detail": f"This endpoint requires one of these roles: {', '.join(allowed_roles)}. Your role: {role}"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(self, request, *args, **kwargs)
        return wrapper
    return decorator


def require_manager(view_func):
    """Decorator to restrict access to manager role only."""
    return require_role('manager')(view_func)


def require_staff_or_manager(view_func):
    """Decorator to allow staff and manager roles."""
    return require_role('staff', 'manager')(view_func)


def require_authenticated(view_func):
    """Decorator to require any authenticated user (customer, staff, or manager)."""
    return require_role('customer', 'staff', 'manager')(view_func)
