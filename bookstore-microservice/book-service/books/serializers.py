from rest_framework import serializers
from .models import Book, Publisher, Category


class PublisherSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'address', 'phone', 'email', 'website', 
                  'description', 'is_active', 'books_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'books_count']
    
    def get_books_count(self, obj):
        return obj.books.count()


class CategorySerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    display_name = serializers.CharField(source='get_name_display', read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'display_name', 'description', 'icon', 'color',
                  'is_active', 'order', 'books_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'display_name', 'created_at', 'updated_at', 'books_count']
    
    def get_books_count(self, obj):
        return obj.books.count()


class BookSerializer(serializers.ModelSerializer):
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    category_name = serializers.CharField(source='category.get_name_display', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'image_url', 'price', 'stock', 
                  'description', 'publisher', 'publisher_name', 'category', 
                  'category_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'publisher_name', 'category_name']


class BookDetailSerializer(serializers.ModelSerializer):
    """Serializer với thông tin đầy đủ của Book, Publisher, Category"""
    publisher_detail = PublisherSerializer(source='publisher', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'image_url', 'price', 'stock',
                  'description', 'publisher', 'publisher_detail', 'category',
                  'category_detail', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'publisher_detail', 'category_detail']
