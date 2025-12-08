from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_flutter(request):
    if request.method != 'POST':
        return JsonResponse(
            {"status": False, "message": "Invalid method"},
            status=405,
        )

    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse(
            {
                "username": user.username,
                "status": True,
                "message": "Login success",
                "username": user.username,
                "is_admin": user.is_superuser or user.is_staff,
            },
            status=200,
        )

    return JsonResponse(
        {
            "status": False,
            "message": "Invalid username or password",
        },
        status=401,
    )
