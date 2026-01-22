from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='اسم الفئة')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name='الوصف')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='صورة الفئة')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:  # إذا كان slug فارغاً
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class Product(models.Model):
    MATERIAL_CHOICES = (
        ('gold', 'ذهب'),
        ('silver', 'فضة'),
        ('diamond', 'ألماس'),
        ('platinum', 'بلاتين'),
        ('pearl', 'لؤلؤ'),
    )
    
    GENDER_CHOICES = (
        ('men', 'رجالي'),
        ('women', 'نسائي'),
        ('unisex', 'للجنسين'),
    )
    
    name = models.CharField(max_length=200, verbose_name='اسم المنتج')
    
    slug = models.SlugField(max_length=200, unique=True, blank=False, null=False)  # أضف blank=False, null=False

    description = models.TextField(verbose_name='الوصف')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='الفئة')
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, verbose_name='المادة')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex', verbose_name='النوع')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='السعر')
    weight = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True, verbose_name='الوزن (جرام)')
    stock = models.PositiveIntegerField(default=0, verbose_name='الكمية المتاحة')
    image = models.ImageField(upload_to='products/', verbose_name='الصورة الرئيسية')
    is_featured = models.BooleanField(default=False, verbose_name='مميز')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'منتج'
        verbose_name_plural = 'المنتجات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', args=[self.slug])

    def save(self, *args, **kwargs):
        # إذا كان slug فارغاً، إنشئه من الاسم
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    is_default = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'صورة المنتج'
        verbose_name_plural = 'صور المنتجات'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تقييم'
        verbose_name_plural = 'التقييمات'
        ordering = ['-created_at']