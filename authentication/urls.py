from django.urls import path
from authentication.views import register, login_user, logout_user, register_api

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('api/register/', register_api, name='register_api'),
]
