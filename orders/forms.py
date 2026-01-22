from django import forms
from .models import Order, ShippingAddress

class OrderCreateForm(forms.ModelForm):
    use_existing_address = forms.BooleanField(
        required=False,
        initial=False,
        label='استخدام عنوان محفوظ'
    )
    shipping_address = forms.ModelChoiceField(
        queryset=ShippingAddress.objects.none(),
        required=False,
        label='اختر العنوان'
    )
    
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'payment_method', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'full_name': 'الاسم الكامل',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
            'city': 'المدينة',
            'payment_method': 'طريقة الدفع',
            'notes': 'ملاحظات إضافية',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['shipping_address'].queryset = ShippingAddress.objects.filter(user=user)
            # تعيين القيم الأولية من الملف الشخصي
            self.fields['full_name'].initial = f"{user.first_name} {user.last_name}"
            self.fields['email'].initial = user.email
            if hasattr(user, 'profile'):
                self.fields['phone'].initial = user.profile.phone
                self.fields['address'].initial = user.profile.address
                self.fields['city'].initial = user.profile.city

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'phone', 'address', 'city', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
        }