import os

from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
import requests

from .models import Customer, UserProfile
from .serializers import CustomerSerializer, RegisterSerializer, RoleTokenObtainPairSerializer, ChangePasswordSerializer

CART_SERVICE_URL = "http://cart-service:8000"
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")


class IsManagerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}


class IsOwnerOrManagerStaff(permissions.BasePermission):
    """Allow customers to access their own record; managers/staff can access all."""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        role = request.auth.get("role") if request.auth else None
        if role in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}:
            return True
        # Customer can only access their own record
        profile = getattr(request.user, "profile", None)
        if profile and profile.customer_id == obj.id:
            return True
        return False


class CustomerListCreate(APIView):
    permission_classes = [IsManagerOrStaff]

    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()

            # Best-effort cart creation for new customers.
            try:
                requests.post(
                    f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": customer.id},
                    headers={"X-Internal-Token": INTERNAL_SERVICE_TOKEN},
                    timeout=3,
                )
            except requests.RequestException:
                pass

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetail(APIView):
    permission_classes = [IsOwnerOrManagerStaff]

    def get_object(self, customer_id):
        try:
            return Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return None

    def get(self, request, customer_id):
        customer = self.get_object(customer_id)
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, customer)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

    def patch(self, request, customer_id):
        customer = self.get_object(customer_id)
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, customer)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, customer_id):
        return self.patch(request, customer_id)

    def delete(self, request, customer_id):
        role = request.auth.get("role") if request.auth else None
        if role != UserProfile.ROLE_MANAGER:
            return Response({"error": "Only managers can delete customers"}, status=status.HTTP_403_FORBIDDEN)
        customer = self.get_object(customer_id)
        if not customer:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, customer_id):
        # Only the customer themselves can change their password
        profile = getattr(request.user, "profile", None)
        if profile is None or profile.customer_id != customer_id:
            return Response({"error": "You can only change your own password"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        current_password = serializer.validated_data["current_password"]
        new_password = serializer.validated_data["new_password"]

        if not request.user.check_password(current_password):
            return Response({"error": "Mật khẩu hiện tại không đúng"}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({"success": True, "message": "Đổi mật khẩu thành công"})


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user, profile = serializer.save()

        if profile.customer_id is not None:
            try:
                requests.post(
                    f"{CART_SERVICE_URL}/carts/",
                    json={"customer_id": profile.customer_id},
                    headers={"X-Internal-Token": INTERNAL_SERVICE_TOKEN},
                    timeout=3,
                )
            except requests.RequestException:
                pass

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": profile.role,
                "customer_id": profile.customer_id,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RoleTokenObtainPairSerializer
