from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'price', 'stock')
    search_fields = ('title', 'author')
    list_filter = ('author',)
    ordering = ('-id',)
    
    fieldsets = (
        ('Thông Tin Sách', {
            'fields': ('title', 'author')
        }),
        ('Giá & Kho', {
            'fields': ('price', 'stock')
        }),
    )
