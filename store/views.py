from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Review
from cart.forms import CartAddProductForm

def home(request):
    """الصفحة الرئيسية"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(is_active=True)[:6]
    
    # إحصائيات الفئات للعرض
    category_stats = {}
    for category in categories:
        category_stats[category.slug] = {
            'count': category.products.count(),
            'name': category.name,
            'slug': category.slug
        }
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
        'category_stats': category_stats,
    }
    
    return render(request, 'store/home.html', context)
def product_list(request):
    """قائمة جميع المنتجات"""
    products = Product.objects.filter(is_active=True)
    
    # البحث
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(material__icontains=query)
        )
    
    # التصفية حسب الفئة
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # التصفية حسب المادة
    material = request.GET.get('material')
    if material:
        products = products.filter(material=material)
    
    # التصفية حسب النوع
    gender = request.GET.get('gender')
    if gender:
        products = products.filter(gender=gender)
    
    # الترتيب
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')
    
    # التقسيم للصفحات
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 12)  # 12 منتج في الصفحة
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True),
    }
    
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """تفاصيل المنتج"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    # نموذج إضافة للسلة
    cart_product_form = CartAddProductForm()
    
    # التقييمات
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    context = {
        'product': product,
        'related_products': related_products,
        'cart_product_form': cart_product_form,
        'reviews': reviews,
    }
    
    return render(request, 'store/product_detail.html', context)

def category_list(request):
    """قائمة الفئات"""
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'store/category_list.html', context)

def category_detail(request, slug):
    try:
        category = Category.objects.get(slug=slug, is_active=True)
        products = category.products.filter(is_active=True)
        
        # فلترة حسب المادة إذا كانت موجودة في الطلب
        material = request.GET.get('material')
        if material:
            products = products.filter(material=material)
        
        # فلترة حسب النوع إذا كان موجوداً في الطلب
        gender = request.GET.get('gender')
        if gender:
            products = products.filter(gender=gender)
        
        # ترتيب حسب السعر
        sort_by = request.GET.get('sort')
        if sort_by == 'price_low':
            products = products.order_by('price')
        elif sort_by == 'price_high':
            products = products.order_by('-price')
        elif sort_by == 'newest':
            products = products.order_by('-created_at')
        else:
            products = products.order_by('name')
        
        # الحصول على القيم الفريدة للفلترة
        materials = products.values_list('material', flat=True).distinct()
        genders = products.values_list('gender', flat=True).distinct()
        
        context = {
            'category': category,
            'products': products,
            'materials': materials,
            'genders': genders,
            'current_material': material,
            'current_gender': gender,
            'sort_by': sort_by,
        }
        
        return render(request, 'store/category_detail.html', context)
    
    except Category.DoesNotExist:
        return render(request, 'store/404.html', status=404)

def add_review(request, product_id):
    """إضافة تقييم للمنتج"""
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment
            )
    
    return redirect('product_detail', slug=product.slug)


from django.shortcuts import render, redirect
from store.forms import ProductForm, MultipleImagesForm
from store.models import Product, ProductImage

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        images_form = MultipleImagesForm(request.POST, request.FILES)
        
        if form.is_valid() and images_form.is_valid():
            product = form.save()

            # رفع الصور المتعددة
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            
            return redirect('dashboard:products_list')
    else:
        form = ProductForm()
        images_form = MultipleImagesForm()
    
    return render(request, 'dashboard/product_add.html', {'form': form, 'images_form': images_form})
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import ProductForm

@login_required
def product_list_dashboard(request):
    products = Product.objects.all()
    return render(request, 'dashboard/products_list.html', {'products': products})

@login_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_edit.html', {'form': form, 'product': product})

@login_required
def product_duplicate(request, product_id):
    original = get_object_or_404(Product, id=product_id)
    product_copy = Product.objects.get(id=product_id)
    product_copy.id = None
    product_copy.slug = f"{original.slug}-copy"
    product_copy.name = f"{original.name} (نسخة)"
    product_copy.save()
    return redirect('products_list')

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('products_list')



def clean_cart(request):
    """حذف المنتجات غير الموجودة أو غير صالحة من السلة"""
    cart = request.session.get('cart', {})
    
    from store.models import Product
    
    # الحصول على قائمة IDs للمنتجات الموجودة فعلًا
    product_ids = Product.objects.values_list('id', flat=True)
    
    # تصفية السلة
    cart = {k: v for k, v in cart.items() if int(k) in product_ids}
    
    request.session['cart'] = cart
    return redirect('cart:cart_detail')