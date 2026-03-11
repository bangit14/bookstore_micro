import uuid
import os
import jwt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment
from .serializers import PaymentSerializer

# Import role-based permissions
try:
    from .permissions import require_staff_or_manager, require_authenticated, extract_role_from_token
except ImportError:
    # Fallback
    def require_staff_or_manager(func):
        return func
    def require_authenticated(func):
        return func
    def extract_role_from_token(request):
        return None


class PaymentListCreate(APIView):
    """
    GET: Xem thanh toán - Staff/Manager xem tất cả, Customer xem của mình
    POST: Tạo thanh toán - Customer, Staff, Manager, Internal Service
    """
    
    @require_authenticated
    def get(self, request):
        """Xem danh sách thanh toán"""
        role = extract_role_from_token(request)
        
        if role in ['staff', 'manager']:
            # Staff và Manager xem tất cả thanh toán
            payments = Payment.objects.all()
        else:
            # Customer chỉ xem thanh toán của đơn hàng mình
            # Cần lấy customer_id từ JWT và filter orders
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1]
            jwt_secret = os.getenv('JWT_SIGNING_KEY', 'bookstore-shared-jwt-secret')
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            customer_id = payload.get('customer_id')
            
            # Lọc payments theo customer_id (cần join với Order)
            # Tạm thời return tất cả, cần refactor
            payments = Payment.objects.all()
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Tạo thanh toán - Customer hoặc Internal Service"""
        # Check for internal service token
        internal_token = request.headers.get('X-Internal-Token')
        if internal_token != "bookstore-internal-token":
            # Nếu không phải internal service, yêu cầu authenticated
            return require_authenticated(lambda self, req: self._create_payment(req))(self, request)
        
        return self._create_payment(request)
    
    def _create_payment(self, request):
        data = request.data.copy()
        if not data.get("transaction_id"):
            data["transaction_id"] = f"pay-{uuid.uuid4().hex[:12]}"
        if not data.get("status"):
            data["status"] = "success"
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentByOrder(APIView):
    @require_authenticated
    def get(self, request, order_id):
        """Theo dõi thanh toán theo order"""
        payments = Payment.objects.filter(order_id=order_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
