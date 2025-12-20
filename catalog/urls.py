from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # ===== JSON API (FLUTTER) =====
    path('json/', views.products_json, name='products_json'),
    path('json/filtered/', views.products_filtered_json, name='products_filtered_json'),
    path('edit/<int:id>/', views.edit_product, name='edit_product'),
    path('create/', views.product_create, name='product_create'),
    path('delete/<int:pk>/', views.product_delete, name='product_delete'),
    path('review/<int:pk>/', views.get_reviews, name='get_reviews'),

    # ===== HTML (WEB ONLY) =====
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
]
