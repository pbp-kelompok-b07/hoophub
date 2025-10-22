from django.urls import path
from review.views import show_review, show_json, create_review, edit_review

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show_review'),
    path('json/', show_json, name='show_json'),
    path('create-review/', create_review, name='create_review'),
    path('<uuid:review_id>/edit', edit_review, name='edit_review')
]