from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('cancel/<int:order_id>/', views.order_cancel, name='order_cancel'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/delete/<int:address_id>/', views.address_delete, name='address_delete'),
]