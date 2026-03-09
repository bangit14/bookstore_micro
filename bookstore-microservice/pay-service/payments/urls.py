from django.urls import path
from .views import PaymentByOrder, PaymentListCreate
urlpatterns = [
    path("payments/", PaymentListCreate.as_view(), name="payments"),
    path("payments/order/<int:order_id>/", PaymentByOrder.as_view(), name="payments-by-order"),
]
