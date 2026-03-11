from django.contrib import admin
from .models import Shipment


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'status', 'tracking_code', 'created_at')
    search_fields = ('order_id', 'tracking_code', 'shipping_address')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông Tin Đơn Hàng', {
            'fields': ('order_id', 'status', 'tracking_code')
        }),
        ('Địa Chỉ Giao Hàng', {
            'fields': ('shipping_address',)
        }),
        ('Thời Gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
