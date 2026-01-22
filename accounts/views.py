from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    """تسجيل مستخدم جديد"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # تحديث الملف الشخصي
            user.profile.phone = form.cleaned_data.get('phone')
            user.profile.save()
            
            # تسجيل الدخول تلقائياً
            login(request, user)
            
            messages.success(request, 'تم إنشاء حسابك بنجاح! مرحباً بك في TIVE.')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    """تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً بعودتك {username}!')
                
                # توجيه المديرين للوحة التحكم
                if user.profile.user_type == 'admin' or user.is_staff:
                    return redirect('dashboard')
                return redirect('profile')
            else:
                messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    """تسجيل الخروج"""
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('home')

@login_required
def profile(request):
    """الصفحة الشخصية للمستخدم"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def wishlist(request):
    """قائمة المفضلة"""
    # قم بتطبيق المنطق الخاص بقائمة المفضلة هنا
    return render(request, 'accounts/wishlist.html')

@login_required
def addresses(request):
    """عناوين المستخدم"""
    # قم بتطبيق المنطق الخاص بالعناوين هنا
    return render(request, 'accounts/addresses.html')

@login_required
def notifications(request):
    """إشعارات المستخدم"""
    # قم بتطبيق المنطق الخاص بالإشعارات هنا
    return render(request, 'accounts/notifications.html')