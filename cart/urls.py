from django.urls import path
from cart.views import show_cart, remove_from_cart, show_checkout, add_to_cart

app_name = 'cart'

urlpatterns = [
    path('', show_cart, name='show_cart'),
    path('checkout/', show_checkout, name='show_checkout'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('<int:id>/delete', remove_from_cart, name='remove_from_cart'),

]