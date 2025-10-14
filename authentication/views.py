from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def register(request):
    if request.method == "GET":
        form = UserCreationForm()
        context = {'form': form}
        return render(request, 'register.html', context)

    elif request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Account created successfully!'})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

def login_user(request):
    if request.method == "GET":
        form = AuthenticationForm()
        context = {'form': form}
        return render(request, 'login.html', context)
    
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = JsonResponse({'success': True, 'message': 'Login successful!'})
            return response
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

def logout_user(request):
    logout(request)
    response = JsonResponse({'success': True, 'message': 'Logged out successfully!'})
    return response