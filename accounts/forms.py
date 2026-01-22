from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='البريد الإلكتروني')
    first_name = forms.CharField(label='الاسم الأول')
    last_name = forms.CharField(label='اسم العائلة')
    phone = forms.CharField(label='رقم الهاتف', max_length=15)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='البريد الإلكتروني')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city']