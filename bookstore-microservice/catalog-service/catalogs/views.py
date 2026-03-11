from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product
from .serializers import ProductSerializer
from .permissions import require_staff_or_manager, require_authenticated


class ProductListCreate(APIView):
    """
    GET: Xem danh sách sản phẩm - Customer, Staff, Manager
    POST: Thêm sản phẩm mới - Staff, Manager only
    """
    
    @require_authenticated
    def get(self, request):
        """Customer, Staff, Manager có thể xem sản phẩm"""
        serializer = ProductSerializer(Product.objects.all(), many=True)
        return Response(serializer.data)
    
    @require_staff_or_manager
    def post(self, request):
        """Chỉ Staff và Manager có thể thêm sản phẩm"""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
