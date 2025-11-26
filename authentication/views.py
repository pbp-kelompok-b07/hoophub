from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

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
    next_url = request.POST.get('next') or reverse('main:show_main')
    if request.method == "GET":
        form = AuthenticationForm()
        context = {'form': form, 'next_url': next_url}
        return render(request, 'login.html', context)
    
    elif request.method == 'POST':
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            response = JsonResponse({'success': True, 'message': 'Login successful!', 'next_url': next_url})
            return response
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=405)

def logout_user(request):
    logout(request)
    response = JsonResponse({'success': True, 'message': 'Logged out successfully!'})
    return response