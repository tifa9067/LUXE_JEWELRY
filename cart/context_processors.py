from .views import _get_cart

def cart(request):
    """إضافة السلة إلى جميع القوالب"""
    cart = _get_cart(request)
    return {'cart': cart}