from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),  # admin CRUD
    path('view/', views.product_view, name='product_view'),  # user/public
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('json/', views.products_json, name='products_json'), 
]