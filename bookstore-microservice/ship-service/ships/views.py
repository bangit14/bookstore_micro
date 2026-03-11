import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Shipment
from .serializers import ShipmentSerializer

# Import role-based permissions
try:
    from .permissions import require_staff_or_manager, require_authenticated
except ImportError:
    # Fallback nếu chưa có permissions.py
    def require_staff_or_manager(func):
        return func
    def require_authenticated(func):
        return func


class ShipmentListCreate(APIView):
    """
    GET: Xem tất cả vận chuyển - Staff, Manager
    POST: Tạo đơn vận chuyển - Staff, Manager, Internal Service
    """
    
    @require_staff_or_manager
    def get(self, request):
        """Staff và Manager xem tất cả đơn vận chuyển"""
        serializer = ShipmentSerializer(Shipment.objects.all(), many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Tạo đơn vận chuyển - cho phép Internal Service (không cần JWT)"""
        # Check for internal service token
        internal_token = request.headers.get('X-Internal-Token')
        if internal_token != "bookstore-internal-token":
            # Nếu không phải internal service, yêu cầu Staff/Manager
            return require_staff_or_manager(lambda self, req: self._create_shipment(req))(self, request)
        
        return self._create_shipment(request)
    
    def _create_shipment(self, request):
        data = request.data.copy()
        if not data.get("tracking_code"):
            data["tracking_code"] = f"trk-{uuid.uuid4().hex[:10]}"
        serializer = ShipmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentByOrder(APIView):
    @require_staff_or_manager
    def get(self, request, order_id):
        """Theo dõi giao hàng - Staff, Manager"""
        serializer = ShipmentSerializer(Shipment.objects.filter(order_id=order_id), many=True)
        return Response(serializer.data)
