from django.urls import path
from review.views import show_review, show_json, show_json_by_id, create_review, edit_review, delete_review, proxy_image, show_json_flutter, show_json_all_flutter, create_review_flutter, edit_review_flutter, delete_review_flutter

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show_review'),
    path('json/', show_json, name='show_json'),
    path('json/<uuid:review_id>/', show_json_by_id, name='show_json_by_id'),
    path('create/<int:id>/', create_review, name='create_review'),
    path('edit/<uuid:review_id>/', edit_review, name='edit_review'),
    path('delete/<uuid:review_id>/', delete_review, name='delete_review'),
    path('proxy-image/', proxy_image, name='proxy_image'),
    path('json-flutter/', show_json_flutter, name='show_json_flutter'),
    path('json-all-flutter/', show_json_all_flutter, name='show_json_all_flutter'),
    path('create-flutter/<int:id>/', create_review_flutter, name='create_review_flutter'),
    path('edit-flutter/<uuid:review_id>/', edit_review_flutter, name='edit_review_flutter'),
    path('delete-flutter/<uuid:review_id>/', delete_review_flutter, name='delete_review_flutter')
]