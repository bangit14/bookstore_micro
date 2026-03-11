from django.urls import path
from .views import CartListCreate, CartByCustomer, CartItemListCreate, CartItemDetail

urlpatterns = [
    path("carts/", CartListCreate.as_view(), name="cart-list-create"),
    path("carts/<int:customer_id>/", CartByCustomer.as_view(), name="cart-by-customer"),
    path("cart-items/", CartItemListCreate.as_view(), name="cart-item-list-create"),
    path("cart-items/<int:item_id>/", CartItemDetail.as_view(), name="cart-item-detail"),
]
