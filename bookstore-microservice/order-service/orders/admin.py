from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product_id', 'quantity', 'unit_price')
    readonly_fields = ('unit_price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'status', 'total_amount', 'created_at')
    search_fields = ('customer_id', 'shipping_address')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Thông Tin Đơn Hàng', {
            'fields': ('customer_id', 'status', 'total_amount')
        }),
        ('Giao Hàng', {
            'fields': ('shipping_address',)
        }),
        ('Thời Gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_id', 'quantity', 'unit_price')
    list_filter = ('order__status',)
    search_fields = ('product_id', 'order__id')
