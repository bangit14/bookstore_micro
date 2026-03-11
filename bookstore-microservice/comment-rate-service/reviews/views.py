from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Review
from .serializers import ReviewSerializer

# Import role-based permissions
try:
    from .permissions import require_authenticated
except ImportError:
    def require_authenticated(func):
        return func


class ReviewListCreate(APIView):
    """
    Đánh giá sản phẩm
    GET: Xem đánh giá - Tất cả (kể cả không đăng nhập)
    POST: Viết đánh giá - Customer, Staff, Manager
    """
    
    def get(self, request):
        """Tất cả có thể xem đánh giá"""
        serializer = ReviewSerializer(Review.objects.all(), many=True)
        return Response(serializer.data)
    
    @require_authenticated
    def post(self, request):
        """Customer, Staff, Manager có thể viết đánh giá"""
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
