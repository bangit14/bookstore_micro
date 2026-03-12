from django.contrib import admin
from .models import Book, Publisher, Category


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'is_active', 'created_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    
    fieldsets = (
        ('Thông Tin Cơ Bản', {
            'fields': ('name', 'email', 'phone', 'website')
        }),
        ('Địa Chỉ & Mô Tả', {
            'fields': ('address', 'description')
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_display_name', 'name', 'icon', 'color', 'order', 'is_active', 'created_at')
    search_fields = ('name', 'display_name', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Thông Tin Thể Loại', {
            'fields': ('name', 'display_name', 'description')
        }),
        ('Hiển Thị', {
            'fields': ('icon', 'color', 'order')
        }),
        ('Trạng Thái', {
            'fields': ('is_active',)
        }),
    )
    
    def get_display_name(self, obj):
        return obj.get_name_display()
    get_display_name.short_description = 'Tên Hiển Thị'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'publisher', 'category', 'price', 'stock', 'created_at')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('publisher', 'category', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông Tin Sách', {
            'fields': ('title', 'author', 'isbn', 'image_url')
        }),
        ('Phân Loại', {
            'fields': ('publisher', 'category')
        }),
        ('Giá & Kho', {
            'fields': ('price', 'stock')
        }),
        ('Mô Tả', {
            'fields': ('description',)
        }),
    )
