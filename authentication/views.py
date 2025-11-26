from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json


@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": False, "message": "Invalid request method."},
            status=405,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": False, "message": "Invalid JSON body."},
            status=400,
        )

    username = (data.get("username") or "").strip()
    password1 = data.get("password1") or ""
    password2 = data.get("password2") or ""

    # validasi basic
    if not username or not password1 or not password2:
        return JsonResponse(
            {"status": False, "message": "Semua field wajib diisi."},
            status=400,
        )

    if password1 != password2:
        return JsonResponse(
            {"status": False, "message": "Password dan konfirmasi tidak cocok."},
            status=400,
        )

    if len(password1) < 8:
        return JsonResponse(
            {"status": False, "message": "Password minimal 8 karakter."},
            status=400,
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"status": False, "message": "Username sudah digunakan."},
            status=400,
        )

    user = User.objects.create_user(username=username, password=password1)
    user.save()

    return JsonResponse(
        {
            "status": "success",           # <- ini yang dicek di Flutter
            "message": "User created successfully!",
            "username": user.username,
        },
        status=200,
    )


@csrf_exempt
def login_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": False, "message": "Invalid request method."},
            status=405,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": False, "message": "Invalid JSON body."},
            status=400,
        )

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse(
            {"status": False, "message": "Username atau password salah."},
            status=401,
        )

    login(request, user)
    return JsonResponse(
        {
            "status": True,
            "message": "Login berhasil.",
            "username": user.username,
        },
        status=200,
    )


@csrf_exempt
def logout_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": False, "message": "Invalid request method."},
            status=405,
        )

    logout(request)
    return JsonResponse(
        {"status": True, "message": "Logout berhasil."},
        status=200,
    )
