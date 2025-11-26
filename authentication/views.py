from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login as auth_login


@csrf_exempt
def register(request):
    # --- GET: register via HTML (Django biasa) ---
    if request.method == "GET":
        form = UserCreationForm()
        context = {"form": form}
        return render(request, "register.html", context)

    # --- POST: bisa dari Flutter (JSON) atau dari form biasa ---
    if request.method == "POST":
        # 1) Kalau datang dari Flutter Web: content-type = application/json
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except json.JSONDecodeError:
                return JsonResponse(
                    {"status": "error", "message": "Invalid JSON body."},
                    status=400,
                )

            username = data.get("username", "").strip()
            password1 = data.get("password1", "")
            password2 = data.get("password2", "")

            if not username or not password1 or not password2:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "All fields (username, password1, password2) are required.",
                    },
                    status=400,
                )

            if password1 != password2:
                return JsonResponse(
                    {"status": "error", "message": "Passwords do not match."},
                    status=400,
                )

            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {"status": "error", "message": "Username already exists."},
                    status=400,
                )

            User.objects.create_user(username=username, password=password1)

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Account created successfully.",
                },
                status=200,
            )

        # 2) Kalau POST dari form HTML biasa (Django)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Account created successfully.",
                },
                status=200,
            )
        return JsonResponse(
            {"status": "error", "errors": form.errors},
            status=400,
        )

    return JsonResponse(
        {"status": "error", "message": "Invalid request method."},
        status=405,
    )


@csrf_exempt
def login_user(request):
    next_url = request.POST.get("next") or reverse("main:show_main")

    if request.method == "GET":
        form = AuthenticationForm()
        context = {"form": form, "next_url": next_url}
        return render(request, "login.html", context)

    elif request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return JsonResponse(
                {
                    "status": True,  # pakai 'status' biar cocok dengan CookieRequest
                    "message": "Login successful!",
                    "next_url": next_url,
                },
                status=200,
            )
        else:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Login failed, please check your username or password.",
                    "errors": form.errors,
                },
                status=401,
            )

    return JsonResponse(
        {"status": False, "message": "Invalid request"},
        status=405,
    )
@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse(
        {"status": True, "message": "Logged out successfully!"},
        status=200,
    )
@csrf_exempt
def flutter_login(request):
    if request.method != 'POST':
        return JsonResponse(
            {"status": False, "message": "Only POST method is allowed."},
            status=405,
        )

    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        auth_login(request, user)
        return JsonResponse(
            {
                "status": True,
                "username": user.username,
                "message": "Login successful!",
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": False,
            "message": "Login failed, please check your username or password.",
        },
        status=401,
    )
