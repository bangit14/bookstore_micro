import os
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from .permissions import require_authenticated, require_staff_or_manager, extract_role_from_token
import jwt

PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "bookstore-internal-token")

def _internal_headers():
    return {"X-Internal-Token": INTERNAL_SERVICE_TOKEN}


class OrderListCreate(APIView):
    """
    GET: 
      - Customer: Chỉ xem đơn hàng của mình
      - Staff/Manager: Xem tất cả đơn hàng
    POST: Tạo đơn hàng - Customer, Staff, Manager
    """
    
    @require_authenticated
    def get(self, request):
        """Xem danh sách đơn hàng"""
        role = extract_role_from_token(request)
        
        if role in ['staff', 'manager']:
            # Staff và Manager xem tất cả đơn hàng
            orders = Order.objects.all()
        else:
            # Customer chỉ xem đơn hàng của mình
            # Lấy customer_id từ JWT token
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1]
            jwt_secret = os.getenv('JWT_SIGNING_KEY', 'bookstore-shared-jwt-secret')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            customer_id = payload.get('customer_id')
            
            if not customer_id:
                return Response(
                    {"error": "Customer ID not found in token"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            orders = Order.objects.filter(customer_id=customer_id)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @require_authenticated
    def post(self, request):
        """Tạo đơn hàng mới - Customer, Staff, Manager"""
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


class OrderDetail(APIView):
    """
    GET /orders/<order_id>/  — Xem chi tiết đơn hàng
    PATCH /orders/<order_id>/ — Cập nhật trạng thái đơn hàng (Staff/Manager)
    """

    @require_authenticated
    def get(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)

    @require_authenticated
    def patch(self, request, order_id):
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
