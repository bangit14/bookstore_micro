from django.urls import path
from .views import OrderListCreate, OrderDetail
urlpatterns = [
    path("orders/", OrderListCreate.as_view(), name="orders"),
    path("orders/<int:order_id>/", OrderDetail.as_view(), name="order-detail"),
]
