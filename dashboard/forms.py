from django import forms
from django.contrib.auth.models import User
from store.models import Product, Category
from orders.models import Order

class ProductFilterForm(forms.Form):
    """نموذج تصفية المنتجات"""
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='الفئة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    material = forms.ChoiceField(
        choices=[('', 'كل المواد')] + list(Product.MATERIAL_CHOICES),
        required=False,
        label='المادة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'كل الحالات')] + [('active', 'نشط'), ('inactive', 'غير نشط')],
        required=False,
        label='الحالة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        label='أقل سعر',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أقل سعر'})
    )
    max_price = forms.DecimalField(
        required=False,
        label='أعلى سعر',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أعلى سعر'})
    )

class OrderFilterForm(forms.Form):
    """نموذج تصفية الطلبات"""
    STATUS_CHOICES = [('', 'كل الحالات')] + list(Order.STATUS_CHOICES)
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label='حالة الطلب',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=[('', 'كل طرق الدفع')] + list(Order.PAYMENT_METHOD_CHOICES),
        required=False,
        label='طريقة الدفع',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        label='من تاريخ',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label='إلى تاريخ',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class UserFilterForm(forms.Form):
    """نموذج تصفية المستخدمين"""
    user_type = forms.ChoiceField(
        choices=[('', 'كل الأنواع')] + [('customer', 'عميل'), ('admin', 'مدير')],
        required=False,
        label='نوع المستخدم',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.ChoiceField(
        choices=[('', 'كل الحالات'), ('active', 'نشط'), ('inactive', 'غير نشط')],
        required=False,
        label='الحالة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )