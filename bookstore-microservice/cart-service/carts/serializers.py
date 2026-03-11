from rest_framework import serializers
from .models import Cart, CartItem


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializer(serializers.ModelSerializer):
    # Explicitly declare cart_id as IntegerField so DRF doesn't confuse it with
    # the FK relation field named 'cart' and silently drop it from validated_data.
    cart_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ["id", "cart_id", "book_id", "quantity"]
