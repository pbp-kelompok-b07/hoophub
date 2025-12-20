from django.urls import path
from wishlist.views import add_to_wishlist, remove_from_wishlist, wishlist_list, toggle_wishlist, show_json, show_json_by_id, proxy_image, add_to_wishlist_flutter, remove_from_wishlist_flutter, toggle_wishlist_flutter

app_name = 'wishlist'

urlpatterns = [
    path('', wishlist_list, name='list'),
    path('add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove/<int:pk>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),
    path("api/json/", show_json, name="show_json"),
    path("api/json/<int:wishlist_id>/", show_json_by_id, name="show_json_by_id"),
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('flutter/add/', add_to_wishlist_flutter, name='add_to_wishlist_flutter'),
    path('flutter/remove/', remove_from_wishlist_flutter, name='remove_from_wishlist_flutter'),
    path('flutter/toggle/', toggle_wishlist_flutter, name='toggle_wishlist_flutter'),
]