from django.urls import path
from cart.views import show_cart, remove_from_cart, show_checkout

# from cart.views import 

app_name = 'cart'

urlpatterns = [
    path('', show_cart, name='show_cart'),
    path('', show_checkout, name='show_checkout'),
    path('<uuid:id>/delete', remove_from_cart, name='remove_from_cart'),
    

]