from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('create/', views.product_create, name='product_create'),
    path('update/<int:pk>/', views.product_update, name='product_update'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('json/', views.products_json, name='products_json'),
    path('review/<int:pk>/', views.get_reviews, name='get_reviews'),
    path('json/filtered/', views.products_filtered_json, name='products_filtered_json'),
]
