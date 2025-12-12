from django.urls import path
from cart.views import show_cart, remove_from_cart, show_checkout, add_to_cart, get_cart_json, delete_cart_flutter, checkout_flutter, add_to_cart_flutter

app_name = 'cart'

urlpatterns = [
    path('', show_cart, name='show_cart'),
    path('checkout/', show_checkout, name='show_checkout'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('<int:id>/delete', remove_from_cart, name='remove_from_cart'),
    path('json-flutter/', get_cart_json, name='get_cart_json'),
    path('add-flutter/<int:product_id>/', add_to_cart_flutter, name='add_to_cart_flutter'),
    path('delete-flutter/', delete_cart_flutter, name='delete_cart_flutter'),
    path('checkout-flutter/', checkout_flutter, name='checkout_flutter'),
]