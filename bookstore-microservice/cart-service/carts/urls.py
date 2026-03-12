from django.urls import path
from .views import CartListCreate, CartByCustomer, CartDetail, CartItemListCreate, CartItemDetail

urlpatterns = [
    path("carts/", CartListCreate.as_view(), name="cart-list-create"),
    path("carts/customer/<int:customer_id>/", CartByCustomer.as_view(), name="cart-by-customer"),
    path("carts/<int:cart_id>/", CartDetail.as_view(), name="cart-detail"),
    path("cart-items/", CartItemListCreate.as_view(), name="cart-item-list-create"),
    path("cart-items/<int:item_id>/", CartItemDetail.as_view(), name="cart-item-detail"),
]
