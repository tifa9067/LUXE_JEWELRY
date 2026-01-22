from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'total_price']
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'المجموع'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'full_name', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = ['order_number', 'subtotal', 'shipping', 'total', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    actions = ['mark_as_confirmed', 'mark_as_shipped', 'mark_as_delivered']
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'payment_status')
        }),
        ('معلومات العميل', {
            'fields': ('full_name', 'email', 'phone', 'address', 'city')
        }),
        ('التكلفة', {
            'fields': ('subtotal', 'shipping', 'discount', 'total')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'is_paid', 'paid_at', 'delivered_at')
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, 'تم تأكيد الطلبات المحددة')
    mark_as_confirmed.short_description = 'تأكيد الطلبات المحددة'
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, 'تم تعليم الطلبات كمرسلة')
    mark_as_shipped.short_description = 'تعليم كمرسلة'
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, 'تم تعليم الطلبات كمسلمة')
    mark_as_delivered.short_description = 'تعليم كمسلمة'

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'is_default', 'created_at']
    list_filter = ['city', 'is_default']
    search_fields = ['user__username', 'full_name', 'phone']