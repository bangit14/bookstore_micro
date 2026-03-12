from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Book, Publisher, Category
from .serializers import BookSerializer, BookDetailSerializer, PublisherSerializer, CategorySerializer

# Import role-based permissions
try:
    from .permissions import require_staff_or_manager, require_authenticated
except ImportError:
    # Fallback if permissions not available
    def require_staff_or_manager(func):
        return func
    def require_authenticated(func):
        return func


# ========== Publisher Views ==========

class PublisherListCreate(APIView):
    """
    GET: Xem danh sách nhà xuất bản - Tất cả
    POST: Thêm nhà xuất bản mới - Staff, Manager only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request):
        """Tất cả có thể xem danh sách nhà xuất bản"""
        publishers = Publisher.objects.filter(is_active=True)
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    @require_staff_or_manager
    def post(self, request):
        """Chỉ Staff và Manager có thể thêm nhà xuất bản"""
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublisherDetail(APIView):
    """
    GET: Xem chi tiết nhà xuất bản - Tất cả
    PUT/PATCH: Cập nhật nhà xuất bản - Staff, Manager only
    DELETE: Xóa nhà xuất bản - Staff, Manager only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, id=publisher_id)
        serializer = PublisherSerializer(publisher)
        return Response(serializer.data)

    @require_staff_or_manager
    def put(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, id=publisher_id)
        serializer = PublisherSerializer(publisher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def patch(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, id=publisher_id)
        serializer = PublisherSerializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def delete(self, request, publisher_id):
        publisher = get_object_or_404(Publisher, id=publisher_id)
        publisher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Category Views ==========

class CategoryListCreate(APIView):
    """
    GET: Xem danh sách thể loại - Tất cả
    POST: Thêm thể loại mới - Staff, Manager only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request):
        """Tất cả có thể xem danh sách thể loại"""
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    @require_staff_or_manager
    def post(self, request):
        """Chỉ Staff và Manager có thể thêm thể loại"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    """
    GET: Xem chi tiết thể loại - Tất cả
    PUT/PATCH: Cập nhật thể loại - Staff, Manager only
    DELETE: Xóa thể loại - Staff, Manager only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @require_staff_or_manager
    def put(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def patch(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @require_staff_or_manager
    def delete(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ========== Book Views ==========

class BookListCreate(APIView):
    """
    GET: Xem danh sách sách - Tất cả (kể cả không đăng nhập)
    POST: Thêm sách mới - Staff, Manager only
    """

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request):
        """Tất cả có thể xem danh sách sách"""
        books = Book.objects.all()
        
        # Filter by category if provided
        category_id = request.query_params.get('category')
        if category_id:
            books = books.filter(category_id=category_id)
        
        # Filter by publisher if provided
        publisher_id = request.query_params.get('publisher')
        if publisher_id:
            books = books.filter(publisher_id=publisher_id)
        
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

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        # Use detailed serializer for GET requests
        serializer = BookDetailSerializer(book)
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
