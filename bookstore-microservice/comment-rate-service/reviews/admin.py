from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'product_id', 'rating', 'created_at')
    search_fields = ('customer_id', 'product_id', 'comment')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Thông Tin Đánh Giá', {
            'fields': ('customer_id', 'product_id', 'rating')
        }),
        ('Bình Luận', {
            'fields': ('comment',)
        }),
        ('Thời Gian', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
