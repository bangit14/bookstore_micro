from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Staff
from .serializers import StaffSerializer
import jwt
import os

# Import role-based permissions
try:
    from .permissions import require_manager, require_staff_or_manager
except ImportError:
    def require_manager(func):
        return func
    def require_staff_or_manager(func):
        return func


class StaffProfile(APIView):
    """
    Staff tự xem thông tin của mình (dùng sau khi login để lấy position)
    GET: Staff xem profile của chính mình
    """

    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        token = auth_header.split(" ")[1]
        try:
            jwt_secret = os.getenv("JWT_SIGNING_KEY", "bookstore-shared-jwt-secret")
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            username = payload.get("username")
            role = payload.get("role")
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        if role not in ("staff", "manager"):
            return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        staff = Staff.objects.filter(username=username).first()
        if not staff:
            staff = Staff.objects.filter(email=payload.get("email", "")).first()
        if not staff:
            return Response({"error": "Staff record not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StaffSerializer(staff)
        data = serializer.data
        data.pop("password", None)
        return Response(data)


class StaffListCreate(APIView):
    """
    Quản lý nhân viên - Chỉ Manager
    GET: Xem danh sách nhân viên
    POST: Tạo tài khoản nhân viên mới
    """
    
    @require_manager
    def get(self, request):
        """Chỉ Manager có thể xem danh sách nhân viên"""
        serializer = StaffSerializer(Staff.objects.all(), many=True)
        return Response(serializer.data)
    
    @require_manager
    def post(self, request):
        """Chỉ Manager có thể tạo nhân viên mới"""
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetail(APIView):
    """
    Chi tiết nhân viên - Chỉ Manager
    GET: Xem chi tiết nhân viên
    PUT/PATCH: Cập nhật nhân viên
    DELETE: Xóa nhân viên
    """
    
    @require_manager
    def get(self, request, staff_id):
        """Xem chi tiết nhân viên"""
        staff = get_object_or_404(Staff, id=staff_id)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    
    @require_manager
    def put(self, request, staff_id):
        """Cập nhật toàn bộ thông tin nhân viên"""
        staff = get_object_or_404(Staff, id=staff_id)
        serializer = StaffSerializer(staff, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @require_manager
    def patch(self, request, staff_id):
        """Cập nhật một phần thông tin nhân viên"""
        staff = get_object_or_404(Staff, id=staff_id)
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @require_manager
    def delete(self, request, staff_id):
        """Xóa nhân viên"""
        staff = get_object_or_404(Staff, id=staff_id)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
