from django.db import models
from django.conf import settings
from store.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد الانتظار'),
        ('confirmed', 'تم التأكيد'),
        ('processing', 'قيد المعالجة'),
        ('shipped', 'تم الشحن'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي'),
        ('refunded', 'تم الاسترجاع'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'الدفع عند الاستلام'),
        ('card', 'بطاقة ائتمان'),
        ('bank', 'تحويل بنكي'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True, verbose_name='رقم الطلب')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='حالة الطلب')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='طريقة الدفع')
    payment_status = models.BooleanField(default=False, verbose_name='حالة الدفع')
    
    # معلومات العميل
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    address = models.TextField(verbose_name='العنوان')
    city = models.CharField(max_length=100, verbose_name='المدينة')
    
    # التكلفة
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المجموع الفرعي')
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='رسوم الشحن')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الخصم')
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='المجموع النهائي')
    
    # معلومات إضافية
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    is_paid = models.BooleanField(default=False, verbose_name='تم الدفع')
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الطلب')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الدفع')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ التسليم')
    
    class Meta:
        verbose_name = 'طلب'
        verbose_name_plural = 'الطلبات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"طلب #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import datetime
            now = datetime.datetime.now()
            self.order_number = f"ORD-{now.strftime('%Y%m%d')}-{Order.objects.filter(created_at__date=now.date()).count() + 1:04d}"
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='المنتج')
    quantity = models.PositiveIntegerField(verbose_name='الكمية')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')
    
    class Meta:
        verbose_name = 'عنصر طلب'
        verbose_name_plural = 'عناصر الطلب'
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity

class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100, verbose_name='الاسم الكامل')
    phone = models.CharField(max_length=15, verbose_name='رقم الهاتف')
    address = models.TextField(verbose_name='العنوان')
    city = models.CharField(max_length=100, verbose_name='المدينة')
    is_default = models.BooleanField(default=False, verbose_name='العنوان الافتراضي')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'عنوان الشحن'
        verbose_name_plural = 'عناوين الشحن'
    
    def __str__(self):
        return f"{self.full_name} - {self.city}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # إلغاء تعيين العنوان الافتراضي القديم
            ShippingAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)