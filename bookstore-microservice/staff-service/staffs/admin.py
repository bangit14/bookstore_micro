from django.contrib import admin
from .models import Staff


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'department', 'position', 'is_active')
    search_fields = ('name', 'email', 'department', 'position')
    list_filter = ('department', 'position', 'is_active')
    ordering = ('-id',)
    
    fieldsets = (
        ('Thông Tin Cá Nhân', {
            'fields': ('name', 'email')
        }),
        ('Công Việc', {
            'fields': ('department', 'position', 'is_active')
        }),
    )
