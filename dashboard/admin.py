from django.contrib import admin
from .models import DashboardStat, Notification

@admin.register(DashboardStat)
class DashboardStatAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_orders', 'total_revenue', 'new_customers', 'top_product']
    list_filter = ['date']
    search_fields = ['top_product__name']
    readonly_fields = ['date']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    def has_add_permission(self, request):
        return False