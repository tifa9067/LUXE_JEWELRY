
from django.contrib import admin
from .models import Category, Product, ProductImage, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields: list[str] = ['user', 'rating', 'comment', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    prepopulated_fields = {'slug': ('name',)}   
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'material', 'gender', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active', 'is_featured']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    fieldsets = (
        ('معلومات المنتج', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('المواصفات', {
            'fields': ('material', 'gender', 'price', 'weight')
        }),
        ('المخزون والصور', {
            'fields': ('stock', 'image')
        }),
        ('الحالة والعروض', {
            'fields': ('is_active', 'is_featured')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['productname', 'userusername', 'comment']
    readonly_fields = ['created_at']

