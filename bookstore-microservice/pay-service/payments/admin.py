from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'method', 'status', 'amount', 'created_at')
    search_fields = ('order_id', 'transaction_id')
    list_filter = ('status', 'method', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông Tin Thanh Toán', {
            'fields': ('order_id', 'amount', 'method', 'status')
        }),
        ('Giao Dịch', {
            'fields': ('transaction_id',)
        }),
        ('Thời Gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
