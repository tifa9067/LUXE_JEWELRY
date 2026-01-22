from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import CartAddProductForm
from django.utils import timezone
from .models import Cart, CartItem, Coupon
from store.models import Product

def _get_cart_id(request):
    """الحصول على معرف السلة من الجلسة أو إنشاؤها"""
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart = Cart.objects.create()
        cart_id = cart.id
        request.session['cart_id'] = cart_id
    return cart_id



def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )
        return cart
    return None
@require_POST
def cart_add(request, product_id):
    """إضافة منتج للسلة"""
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        # التحقق من توفر الكمية
        if quantity > product.stock:
            messages.error(request, f'الكمية المطلوبة غير متوفرة. المتاح: {product.stock}')
            return redirect('product_detail', slug=product.slug)
        
        # البحث عن المنتج في السلة
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            if cd['override']:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            
            # التحقق من عدم تجاوز المخزون
            if cart_item.quantity > product.stock:
                cart_item.quantity = product.stock
                messages.warning(request, f'تم تعديل الكمية إلى الحد الأقصى المتاح: {product.stock}')
        
        cart_item.save()
        messages.success(request, f'تم إضافة {product.name} إلى السلة')
    
    return redirect('cart_detail')

def cart_remove(request, product_id):
    """حذف منتج من السلة"""
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        messages.success(request, f'تم حذف {product.name} من السلة')
    except CartItem.DoesNotExist:
        messages.error(request, 'المنتج غير موجود في السلة')
    
    return redirect('cart_detail')

def cart_update(request, product_id):
    """تحديث كمية المنتج في السلة"""
    cart = _get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']
        
        # التحقق من توفر الكمية
        if quantity > product.stock:
            messages.error(request, f'الكمية المطلوبة غير متوفرة. المتاح: {product.stock}')
            return redirect('cart_detail')
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, f'تم تحديث كمية {product.name}')
            else:
                cart_item.delete()
                messages.success(request, f'تم حذف {product.name} من السلة')
        except CartItem.DoesNotExist:
            messages.error(request, 'المنتج غير موجود في السلة')
    
    return redirect('cart_detail')

def cart_detail(request):
    """عرض محتويات السلة"""
    cart = _get_cart(request)
    
    # إضافة نموذج لكل منتج في السلة
    cart_items = []
    for item in cart.items.all():
        form = CartAddProductForm(initial={
            'quantity': item.quantity,
            'override': True
        })
        cart_items.append({
            'item': item,
            'form': form
        })
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    
    return render(request, 'cart/cart.html', context)

def cart_clear(request):
    """تفريغ السلة بالكامل"""
    cart = _get_cart(request)
    cart.items.all().delete()
    messages.success(request, 'تم تفريغ السلة بنجاح')
    return redirect('cart_detail')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        cart = Cart.objects.get(user=request.user)
        
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            
            # التحقق من صلاحية الكوبون
            now = timezone.now()
            if coupon.valid_from <= now <= coupon.valid_to:
                if coupon.used_count < coupon.max_usage:
                    if cart.get_grand_total() >= coupon.min_purchase:
                        # حفظ الكوبون في الجلسة
                        request.session['coupon_id'] = coupon.id
                        request.session['coupon_code'] = coupon.code
                        messages.success(request, f'تم تطبيق كود الخصم {code} بنجاح!')
                    else:
                        messages.error(request, f'الحد الأدنى للشراء لتطبيق هذا الكوبون هو {coupon.min_purchase} ر.س')
                else:
                    messages.error(request, 'تم تجاوز الحد الأقصى لاستخدام هذا الكوبون')
            else:
                messages.error(request, 'الكوبون منتهي الصلاحية')
                
        except Coupon.DoesNotExist:
            messages.error(request, 'كود الخصم غير صحيح')
        
        return redirect('cart:cart_detail')
def remove_coupon(request):
    # كود لإزالة الكوبون من الجلسة أو الطلب
    if 'coupon_id' in request.session:
        del request.session['coupon_id']
        del request.session['coupon_discount']
    
    return redirect('cart:cart_detail')  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from store.models import Product

@login_required
def checkout(request):
    # جلب عربة التسوق للمستخدم الحالي
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # حساب الإجمالي
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        # هنا يمكنك معالجة الدفع وإنشاء الطلب
        # هذا مثال بسيط
        order_number = f"ORD-{request.user.id}-{cart.id}"
        
        # يمكنك هنا:
        # 1. إنشاء نموذج Order
        # 2. تفريغ عربة التسوق
        # 3. إعادة توجيه لصفحة تأكيد الطلب
        
        cart.items.all().delete()  # تفريغ العربة
        return render(request, 'cart/checkout_success.html', {
            'order_number': order_number,
            'total_price': total_price
        })
    
    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'cart': cart
    })  