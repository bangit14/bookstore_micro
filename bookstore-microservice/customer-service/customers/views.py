import os

from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
import requests

from .models import Customer, UserProfile
from .serializers import CustomerSerializer, RegisterSerializer, RoleTokenObtainPairSerializer

CART_SERVICE_URL = "http://cart-service:8000"
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")


class IsManagerOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role = request.auth.get("role") if request.auth else None
        return role in {UserProfile.ROLE_MANAGER, UserProfile.ROLE_STAFF}


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
