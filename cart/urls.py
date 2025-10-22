from django.urls import path
from cart.views import show_cart, delete_from_cart

# from cart.views import 

app_name = 'cart'

urlpatterns = [
    path('', show_cart, name='show_cart'),
    path('/<uuid:id>/delete', delete_from_cart, name='delete_from_cart'),


]