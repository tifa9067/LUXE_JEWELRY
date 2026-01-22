from django.db import models
from django.conf import settings
from orders.models import Order
from store.models import Product

class DashboardStat(models.Model):
    """تخزين الإحصائيات للمديرين"""
    date = models.DateField(unique=True, verbose_name='التاريخ')
    total_orders = models.IntegerField(default=0, verbose_name='إجمالي الطلبات')
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='إجمالي الإيرادات')
    new_customers = models.IntegerField(default=0, verbose_name='عملاء جدد')
    top_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='المنتج الأكثر مبيعاً')
    
    class Meta:
        verbose_name = 'إحصائية يومية'
        verbose_name_plural = 'الإحصائيات اليومية'
        ordering = ['-date']
    
    def __str__(self):
        return f"إحصائيات {self.date}"

class Notification(models.Model):
    """الإشعارات للمديرين"""
    TYPE_CHOICES = (
        ('order', 'طلب جديد'),
        ('low_stock', 'منخفض المخزون'),
        ('payment', 'دفع جديد'),
        ('system', 'نظام'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='المستخدم')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='نوع الإشعار')
    title = models.CharField(max_length=200, verbose_name='العنوان')
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    related_object_id = models.IntegerField(null=True, blank=True, verbose_name='معرف الكائن المرتبط')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"