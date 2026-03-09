from django.urls import path
from .views import AddCartItem, CartCreate, ViewCart

urlpatterns = [
    path("carts/", CartCreate.as_view(), name="create-cart"),
    path("carts/items/", AddCartItem.as_view(), name="add-cart-item"),
    path("carts/<int:customer_id>/", ViewCart.as_view(), name="view-cart"),
]
