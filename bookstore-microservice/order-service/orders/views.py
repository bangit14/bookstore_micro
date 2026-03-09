import os
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")

def _internal_headers():
    return {"X-Internal-Token": INTERNAL_SERVICE_TOKEN}

class OrderListCreate(APIView):
    def get(self, request):
        serializer = OrderSerializer(Order.objects.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()

        payment_payload = {
            "order_id": order.id,
            "amount": str(order.total_amount),
            "method": request.data.get("payment_method", "cod"),
            "status": "success",
        }
        shipment_payload = {
            "order_id": order.id,
            "shipping_address": order.shipping_address,
            "status": "shipping",
        }
        payment_ok = False
        shipment_ok = False
        try:
            p_resp = requests.post(f"{PAY_SERVICE_URL}/payments/", json=payment_payload, headers=_internal_headers(), timeout=5)
            payment_ok = p_resp.status_code in {200, 201}
        except requests.RequestException:
            payment_ok = False
        try:
            s_resp = requests.post(f"{SHIP_SERVICE_URL}/shipments/", json=shipment_payload, headers=_internal_headers(), timeout=5)
            shipment_ok = s_resp.status_code in {200, 201}
        except requests.RequestException:
            shipment_ok = False

        if payment_ok:
            order.status = "paid"
        if shipment_ok:
            order.status = "shipping"
        order.save()

        out = OrderSerializer(order)
        return Response({
            "order": out.data,
            "payment_created": payment_ok,
            "shipment_created": shipment_ok,
        }, status=status.HTTP_201_CREATED)
