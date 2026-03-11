import requests
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .permissions import IsManagerOrStaffOrInternal, IsManagerStaffOrCustomer
from .serializers import CartItemSerializer, CartSerializer

BOOK_SERVICE_URL = "http://book-service:8000"


class CartListCreate(APIView):
    permission_classes = [IsManagerStaffOrCustomer]

    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)

    def post(self, request):
        customer_id = request.data.get("customer_id")
        if customer_id:
            existing = Cart.objects.filter(customer_id=customer_id).first()
            if existing:
                return Response(CartSerializer(existing).data, status=status.HTTP_200_OK)
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartByCustomer(APIView):
    """Returns the Cart object (with its id) for a given customer_id."""
    permission_classes = [IsManagerStaffOrCustomer]

    def get(self, request, customer_id):
        cart = Cart.objects.filter(customer_id=customer_id).first()
        if not cart:
            # Auto-create cart if missing
            cart = Cart.objects.create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemListCreate(APIView):
    permission_classes = [IsManagerStaffOrCustomer]

    def get(self, request):
        cart_id = request.query_params.get("cart_id")
        if cart_id:
            items = CartItem.objects.filter(cart_id=cart_id)
        else:
            items = CartItem.objects.all()
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            cart_id = int(request.data.get("cart_id"))
            book_id = int(request.data.get("book_id"))
        except (TypeError, ValueError):
            return Response(
                {"error": "cart_id and book_id are required integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = int(request.data.get("quantity", 1))

        # If item already in cart, increase quantity instead of duplicating
        existing = CartItem.objects.filter(cart_id=cart_id, book_id=book_id).first()
        if existing:
            existing.quantity += quantity
            existing.save()
            return Response(CartItemSerializer(existing).data, status=status.HTTP_200_OK)

        item = CartItem.objects.create(cart_id=cart_id, book_id=book_id, quantity=quantity)
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemDetail(APIView):
    permission_classes = [IsManagerStaffOrCustomer]

    def get_object(self, item_id):
        return get_object_or_404(CartItem, pk=item_id)

    def patch(self, request, item_id):
        item = self.get_object(item_id)
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, item_id):
        return self.patch(request, item_id)

    def delete(self, request, item_id):
        item = self.get_object(item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
