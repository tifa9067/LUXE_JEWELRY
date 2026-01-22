from django import forms
from .models import Product, Category


# فورم المنتج العادي
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'description', 'price', 'category', 'gender', 
                 'material', 'weight', 'stock', 'image', 'is_active', 'is_featured']
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'material': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'name': 'اسم المنتج',
            'slug': 'رابط المنتج',
            'description': 'الوصف',
            'price': 'السعر (ر.س)',
            'category': 'الفئة',
            'gender': 'النوع',
            'material': 'المادة',
            'weight': 'الوزن (جرام)',
            'stock': 'الكمية المتاحة',
            'image': 'الصورة الرئيسية',
            'is_featured': 'منتج مميز',
            'is_active': 'نشط',
        }
# فورم الصور المتعددة (ليس ModelForm)
from django import forms
from .models import Product, Category
from .widgets import MultipleImageField  # استيراد الودجت المخصص

# ... باقي الكود ...

class MultipleImagesForm(forms.Form):
    images = MultipleImageField(
        required=False,
        label="الصور الإضافية"
    )
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الفئة'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رابط الفئة (إنجليزي)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الفئة'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

        labels = {
            'name': 'اسم الفئة',
            'slug': 'رابط الفئة',
            'description': 'الوصف',
            'image': 'صورة الفئة',
            'is_active': 'نشط',
        }