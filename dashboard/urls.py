
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('products/', views.product_management, name='product_management'),
    path('products/add/', views.product_add, name='product_add'),  # ✅ إضافة هذا
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),  # ✅ إضافة هذا
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),  # ✅ إضافة هذا
    path('products/update-status/<int:product_id>/', views.update_product_status, name='update_product_status'),
    
        path('products/delete/<int:product_id>/', views.product_delete, name='product_duplicate'),
    # إدارة الفئات
    path('categories/', views.category_management, name='category_management'),  # ✅ إضافة هذا
    path('categories/add/', views.category_add, name='category_add'),  # ✅ إضافة هذا
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),  # ✅ إضافة هذا
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),  # ✅ إضافة هذا
    
    path('orders/', views.order_management, name='order_management'),
    path('orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('users/', views.user_management, name='user_management'),
    path('users/toggle-status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('reports/', views.reports, name='reports'),
    
    # الإشعارات
    path('notification/read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notification/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
]