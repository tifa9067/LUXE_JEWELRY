from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from accounts.models import Profile
from store.models import Product, Category
from orders.models import Order, OrderItem  # ✅ تصحيح: استيراد من orders.models
from .forms import ProductFilterForm, OrderFilterForm, UserFilterForm
from .models import Notification

def is_admin(user):
    """التحقق مما إذا كان المستخدم مدير"""
    return user.is_authenticated and user.profile.user_type == 'admin'

def is_superuser(user):
    """التحقق مما إذا كان المستخدم مدير عام"""
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def admin_dashboard(request):
    """لوحة التحكم الرئيسية للمدير"""
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # إحصائيات سريعة
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_products': Product.objects.count(),
        'low_stock_products': Product.objects.filter(stock__lt=10).count(),
        'total_customers': Profile.objects.filter(user_type='customer').count(),
        'total_revenue': Order.objects.filter(status='delivered').aggregate(
            total=Sum('total')
        )['total'] or 0,
    }
    
    # الإيرادات خلال آخر 7 أيام
    revenue_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_revenue = Order.objects.filter(
            created_at__date=date,
            status='delivered'
        ).aggregate(total=Sum('total'))['total'] or 0
        revenue_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'revenue': float(daily_revenue)
        })
    
    # أحدث الطلبات
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # المنتجات الأكثر مبيعاً
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).order_by('-total_sold')[:5]
    
    # الإشعارات غير المقروءة
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'revenue_data': revenue_data,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'notifications': notifications,
        'today': today,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def product_management(request):
    """إدارة المنتجات"""
    products = Product.objects.select_related('category').all()
    form = ProductFilterForm(request.GET or None)
    
    if form.is_valid():
        if form.cleaned_data.get('category'):
            products = products.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('material'):
            products = products.filter(material=form.cleaned_data['material'])
        if form.cleaned_data.get('status'):
            if form.cleaned_data['status'] == 'active':
                products = products.filter(is_active=True)
            else:
                products = products.filter(is_active=False)
        if form.cleaned_data.get('min_price'):
            products = products.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data.get('max_price'):
            products = products.filter(price__lte=form.cleaned_data['max_price'])
    
    context = {
        'products': products,
        'form': form,
    }
    
    return render(request, 'dashboard/products.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def order_management(request):
    """إدارة الطلبات"""
    orders = Order.objects.select_related('user').all()
    form = OrderFilterForm(request.GET or None)
    
    if form.is_valid():
        if form.cleaned_data.get('status'):
            orders = orders.filter(status=form.cleaned_data['status'])
        if form.cleaned_data.get('payment_method'):
            orders = orders.filter(payment_method=form.cleaned_data['payment_method'])
        if form.cleaned_data.get('start_date'):
            orders = orders.filter(created_at__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            orders = orders.filter(created_at__date__lte=form.cleaned_data['end_date'])
    
    # إحصائيات الطلبات
    order_stats = {
        'pending': orders.filter(status='pending').count(),
        'confirmed': orders.filter(status='confirmed').count(),
        'processing': orders.filter(status='processing').count(),
        'shipped': orders.filter(status='shipped').count(),
        'delivered': orders.filter(status='delivered').count(),
    }
    
    context = {
        'orders': orders,
        'form': form,
        'order_stats': order_stats,
    }
    
    return render(request, 'dashboard/orders.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def user_management(request):
    """إدارة المستخدمين"""
    users = Profile.objects.select_related('user').all()
    form = UserFilterForm(request.GET or None)
    
    if form.is_valid():
        if form.cleaned_data.get('user_type'):
            users = users.filter(user_type=form.cleaned_data['user_type'])
        if form.cleaned_data.get('is_active'):
            if form.cleaned_data['is_active'] == 'active':
                users = users.filter(user__is_active=True)
            else:
                users = users.filter(user__is_active=False)
    
    context = {
        'users': users,
        'form': form,
    }
    
    return render(request, 'dashboard/users.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def update_order_status(request, order_id):
    """تحديد حالة الطلب"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            order.save()
            
            # إنشاء إشعار
            Notification.objects.create(
                user=request.user,
                notification_type='order',
                title=f'تحديث حالة الطلب #{order.order_number}',
                message=f'تم تغيير حالة الطلب من {order.get_status_display()} إلى {order.get_status_display()}',
                related_object_id=order.id
            )
            
            messages.success(request, f'تم تحديث حالة الطلب #{order.order_number}')
    
    return redirect('order_management')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def update_product_status(request, product_id):
    """تفعيل/تعطيل المنتج"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product.is_active = not product.is_active
        product.save()
        
        status = "تفعيل" if product.is_active else "تعطيل"
        messages.success(request, f'تم {status} المنتج: {product.name}')
    
    return redirect('product_management')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def toggle_user_status(request, user_id):
    """تفعيل/تعطيل المستخدم"""
    if request.method == 'POST':
        from django.contrib.auth.models import User
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        
        status = "تفعيل" if user.is_active else "تعطيل"
        messages.success(request, f'تم {status} المستخدم: {user.username}')
    
    return redirect('user_management')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def reports(request):
    """التقارير والإحصائيات"""
    # فترة التقرير (آخر 30 يوم)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # بيانات المبيعات اليومية
    sales_data = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_sales = Order.objects.filter(
            created_at__date=current_date,
            status='delivered'
        ).aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total')
        )
        
        sales_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'orders': daily_sales['total_orders'] or 0,
            'revenue': float(daily_sales['total_revenue'] or 0)
        })
        
        current_date += timedelta(days=1)
    
    # المنتجات الأكثر مبيعاً
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity'),
        total_revenue=Sum(F('orderitem__quantity') * F('orderitem__price'))
    ).order_by('-total_sold')[:10]
    
    # العملاء الأكثر شراءً
    top_customers = Profile.objects.filter(user_type='customer').annotate(
        total_orders=Count('user__orders'),
        total_spent=Sum('user__orders__total')
    ).order_by('-total_spent')[:10]
    
    # إحصائيات عامة
    general_stats = {
        'total_orders': Order.objects.filter(
            created_at__date__range=[start_date, end_date]
        ).count(),
        'total_revenue': Order.objects.filter(
            created_at__date__range=[start_date, end_date],
            status='delivered'
        ).aggregate(total=Sum('total'))['total'] or 0,
        'avg_order_value': 0,
        'conversion_rate': 0,
    }
    
    if general_stats['total_orders'] > 0:
        general_stats['avg_order_value'] = general_stats['total_revenue'] / general_stats['total_orders']
    
    context = {
        'sales_data': sales_data,
        'top_products': top_products,
        'top_customers': top_customers,
        'general_stats': general_stats,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'dashboard/reports.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def mark_notification_read(request, notification_id):
    """تحديد الإشعار كمقروء"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('admin_dashboard')

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def mark_all_notifications_read(request):
    """تحديد جميع الإشعارات كمقروءة"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('admin_dashboard')
# ===========================================
# دوال إدارة المنتجات
# ===========================================

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def product_add(request):
    """إضافة منتج جديد"""
    from store.forms import ProductForm
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            
            # حفظ الصور الإضافية إذا وجدت
            images = request.FILES.getlist('additional_images')
            for image in images:
                from store.models import ProductImage
                ProductImage.objects.create(product=product, image=image)
            
            messages.success(request, 'تمت إضافة المنتج بنجاح')
            return redirect('product_management')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'إضافة منتج جديد',
    }
    
    return render(request, 'dashboard/product_form.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def product_edit(request, product_id):
    """تعديل منتج"""
    from store.forms import ProductForm

    
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المنتج بنجاح')
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'تعديل المنتج',
        'product': product,
    }
    
    return render(request, 'dashboard/product_form.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def product_delete(request, product_id):
    """حذف منتج"""

    
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        product_name = product.name
        product.delete()
        messages.success(request, f'تم حذف المنتج: {product_name}')
    
    return redirect('product_management')

# ===========================================
# دوال إدارة الفئات
# ===========================================

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def category_management(request):
    """إدارة الفئات"""
    from store.models import Category
    from store.forms import CategoryForm
    
    categories = Category.objects.all()
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تمت إضافة الفئة بنجاح')
            return redirect('category_management')
    
    context = {
        'categories': categories,
        'form': form,
    }
    
    return render(request, 'dashboard/categories.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def category_add(request):
    """إضافة فئة جديدة"""
    from store.forms import CategoryForm
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تمت إضافة الفئة بنجاح')
            return redirect('category_management')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'إضافة فئة جديدة',
    }
    
    return render(request, 'dashboard/category_form.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def category_edit(request, category_id):
    """تعديل فئة"""
    from store.forms import CategoryForm
    from store.models import Category
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الفئة بنجاح')
            return redirect('category_management')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'title': 'تعديل الفئة',
        'category': category,
    }
    
    return render(request, 'dashboard/category_form.html', context)

@login_required
@user_passes_test(lambda u: is_admin(u) or is_superuser(u))
def category_delete(request, category_id):
    """حذف فئة"""
    from store.models import Category
    
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        
        # التحقق من عدم وجود منتجات في الفئة
        if category.products.exists():
            messages.error(request, 'لا يمكن حذف الفئة لأنها تحتوي على منتجات')
        else:
            category_name = category.name
            category.delete()
            messages.success(request, f'تم حذف الفئة: {category_name}')
    
    return redirect('category_management')