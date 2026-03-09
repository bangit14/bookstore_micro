import uuid
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Payment
from .permissions import IsAuthenticatedOrInternal
from .serializers import PaymentSerializer
class PaymentListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedOrInternal()]
        return [IsAuthenticated()]

    def get(self, request):
        serializer = PaymentSerializer(Payment.objects.all(), many=True)
        return Response(serializer.data)
    def post(self, request):
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
    def get(self, request, order_id):
        payments = Payment.objects.filter(order_id=order_id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
