from django.urls import path
from .views import ShipmentByOrder, ShipmentListCreate
urlpatterns = [
    path("shipments/", ShipmentListCreate.as_view(), name="shipments"),
    path("shipments/order/<int:order_id>/", ShipmentByOrder.as_view(), name="shipments-by-order"),
]
