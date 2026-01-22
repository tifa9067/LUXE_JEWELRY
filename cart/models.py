from django.db import models
from django.conf import settings
from store.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.user:
            return f"سلة {self.user.username}"
        return f"سلة {self.session_key}"
    
    def get_cost(self):
        return self.product.price * self.quantity
    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())
    def get_tax(self):
        """حساب قيمة الضريبة (15%)"""
        return self.get_total_price() * 0.15    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
    def get_tax(self):
        from decimal import Decimal
        return self.get_total_price() * Decimal('0.15')  # استخدام Decimal بدلاً من float

    def get_shipping_cost(self):
        return 0 if self.get_total_price() >= 500 else 50

    def get_grand_total(self):
        return self.get_total_price() + self.get_tax() + self.get_shipping_cost()
    class Meta:
        verbose_name = 'سلة التسوق'
        verbose_name_plural = 'سلال التسوق'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    # def __str__(self):
    #     return f"{self.product.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    class Meta:
        verbose_name = 'عنصر في السلة'
        verbose_name_plural = 'عناصر السلة'
        unique_together = ['cart', 'product']

from django.core.validators import MinValueValidator, MaxValueValidator

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='كود الخصم')
    discount_type = models.CharField(max_length=10, choices=[
        ('percentage', 'نسبة مئوية'),
        ('fixed', 'قيمة ثابتة')
    ], default='percentage', verbose_name='نوع الخصم')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='قيمة الخصم')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='الحد الأدنى للشراء')
    valid_from = models.DateTimeField(verbose_name='صالح من')
    valid_to = models.DateTimeField(verbose_name='صالح حتى')
    max_usage = models.PositiveIntegerField(default=1, verbose_name='الحد الأقصى للاستخدام')
    used_count = models.PositiveIntegerField(default=0, verbose_name='عدد مرات الاستخدام')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    
    class Meta:
        verbose_name = 'كوبون'
        verbose_name_plural = 'الكوبونات'
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (self.is_active and 
                self.valid_from <= now <= self.valid_to and 
                self.used_count < self.max_usage)
    
    def calculate_discount(self, total):
        if not self.is_valid():
            return 0
        
        if self.discount_type == 'percentage':
            discount = total * (self.discount_value / 100)
        else:  # fixed
            discount = self.discount_value
        
        return min(discount, total)
