import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .permissions import IsManagerOrStaffOrInternal, IsManagerStaffOrCustomer
from .serializers import CartItemSerializer, CartSerializer

BOOK_SERVICE_URL = "http://book-service:8000"


class CartCreate(APIView):
    permission_classes = [IsManagerOrStaffOrInternal]

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCartItem(APIView):
    permission_classes = [IsManagerStaffOrCustomer]

    def post(self, request):
        book_id = request.data.get("book_id")
        if book_id is None:
            return Response({"error": "book_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            r = requests.get(f"{BOOK_SERVICE_URL}/books/", timeout=3)
            r.raise_for_status()
            books = r.json()
        except requests.RequestException:
            return Response(
                {"error": "Book service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not any(int(b["id"]) == int(book_id) for b in books):
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCart(APIView):
    permission_classes = [IsManagerStaffOrCustomer]

    def get(self, request, customer_id):
        cart = get_object_or_404(Cart, customer_id=customer_id)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)
