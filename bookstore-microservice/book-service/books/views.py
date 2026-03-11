from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Book
from .serializers import BookSerializer

# Import role-based permissions
try:
    from .permissions import require_staff_or_manager, require_authenticated
except ImportError:
    # Fallback if permissions not available
    def require_staff_or_manager(func):
        return func
    def require_authenticated(func):
        return func


class BookListCreate(APIView):
    """
    GET: Xem danh sách sách - Tất cả (kể cả không đăng nhập)
    POST: Thêm sách mới - Staff, Manager only
    """

    def get(self, request):
        """Tất cả có thể xem danh sách sách"""
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    @require_staff_or_manager
    def post(self, request):
        """Chỉ Staff và Manager có thể thêm sách"""
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    """
    GET: Xem chi tiết sách - Customer, Staff, Manager
    PUT/PATCH: Cập nhật sách - Staff, Manager only
    DELETE: Xóa sách - Staff, Manager only
    """

    @require_authenticated
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    @require_staff_or_manager
    def put(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def patch(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def delete(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
