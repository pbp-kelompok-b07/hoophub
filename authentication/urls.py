from django.urls import path
from authentication.views import register, login_user, logout_user, register_flutter, login_flutter, logout_flutter

app_name = 'authentication'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register-flutter/', register_flutter, name='register_flutter'),
    path('login-flutter/', login_flutter, name='login_flutter'),
    path('logout-flutter/', logout_flutter, name='logout_flutter')
]