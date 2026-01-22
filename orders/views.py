from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from cart.views import _get_cart
from store.models import Product
from .models import Order, OrderItem, ShippingAddress
from .forms import OrderCreateForm, ShippingAddressForm

@login_required
def order_create(request):
    """إنشاء طلب جديد"""
    cart = _get_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, 'سلة التسوق فارغة')
        return redirect('cart_detail')
    
    # التحقق من توفر المنتجات
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            messages.error(request, f'الكمية المطلوبة من {item.product.name} غير متوفرة')
            return redirect('cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # حساب التكلفة
            subtotal = cart.total_price
            shipping = 50  # رسوم شحن ثابتة (يمكن تغييرها)
            total = subtotal + shipping
            
            order.subtotal = subtotal
            order.shipping = shipping
            order.total = total
            
            # حفظ العنوان إذا طلب المستخدم
            if form.cleaned_data.get('use_existing_address') and form.cleaned_data.get('shipping_address'):
                address = form.cleaned_data['shipping_address']
                order.full_name = address.full_name
                order.phone = address.phone
                order.address = address.address
                order.city = address.city
            elif request.user.is_authenticated and not form.cleaned_data.get('save_address'):
                # حفظ العنوان الجديد
                address_form = ShippingAddressForm(request.POST)
                if address_form.is_valid():
                    address = address_form.save(commit=False)
                    address.user = request.user
                    address.save()
            
            order.save()
            
            # إنشاء عناصر الطلب
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                
                # تحديث المخزون
                item.product.stock -= item.quantity
                item.product.save()
            
            # تفريغ السلة
            cart.items.all().delete()
            
            messages.success(request, f'تم إنشاء طلبك بنجاح! رقم الطلب: {order.order_number}')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderCreateForm(user=request.user)
    
    context = {
        'cart': cart,
        'form': form,
        'shipping': 50,  # رسوم الشحن
    }
    
    return render(request, 'orders/order_create.html', context)

@login_required
def order_detail(request, order_id):
    """عرض تفاصيل الطلب"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)

@login_required
def order_list(request):
    """قائمة طلبات المستخدم"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)

@login_required
def order_cancel(request, order_id):
    """إلغاء الطلب"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        # إرجاع المنتجات للمخزون
        for item in order.items.all():
            item.product.stock += item.quantity
            item.product.save()
        
        messages.success(request, 'تم إلغاء الطلب بنجاح')
    else:
        messages.error(request, 'لا يمكن إلغاء الطلب في هذه المرحلة')
    
    return redirect('order_detail', order_id=order.id)

@login_required
def address_list(request):
    """عناوين الشحن للمستخدم"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'تم إضافة العنوان بنجاح')
            return redirect('address_list')
    else:
        form = ShippingAddressForm()
    
    context = {
        'addresses': addresses,
        'form': form,
    }
    
    return render(request, 'orders/address_list.html', context)

@login_required
def address_delete(request, address_id):
    """حذف عنوان"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'تم حذف العنوان بنجاح')
    return redirect('address_list')