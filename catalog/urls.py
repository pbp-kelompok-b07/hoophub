from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # hanya satu route utama /catalog/
    path('', views.product_list, name='product_list'),

    # CRUD
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
     path('<int:pk>/', views.product_detail, name='product_detail'),
    # endpoint JSON (AJAX)
    path('json/', views.products_json, name='products_json'),
]
