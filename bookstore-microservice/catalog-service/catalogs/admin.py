from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'stock')
    search_fields = ('name', 'description', 'category')
    list_filter = ('category',)
    ordering = ('-id',)
    
    fieldsets = (
        ('Thông Tin Sản Phẩm', {
            'fields': ('name', 'description', 'category', 'image_url')
        }),
        ('Giá & Kho', {
            'fields': ('price', 'stock')
        }),
    )
