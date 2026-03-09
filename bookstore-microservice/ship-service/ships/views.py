import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Shipment
from .permissions import IsAuthenticatedOrInternal
from .serializers import ShipmentSerializer
class ShipmentListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedOrInternal()]
        return [IsAuthenticated()]

    def get(self, request):
        serializer = ShipmentSerializer(Shipment.objects.all(), many=True)
        return Response(serializer.data)
    def post(self, request):
        data = request.data.copy()
        if not data.get("tracking_code"):
            data["tracking_code"] = f"trk-{uuid.uuid4().hex[:10]}"
        serializer = ShipmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ShipmentByOrder(APIView):
    def get(self, request, order_id):
        serializer = ShipmentSerializer(Shipment.objects.filter(order_id=order_id), many=True)
        return Response(serializer.data)
