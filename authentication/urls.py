from django.urls import path
from .views import register, login_user, logout_user,flutter_login

app_name = "authentication"

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("flutter-login/", flutter_login, name="flutter_login"),
]
