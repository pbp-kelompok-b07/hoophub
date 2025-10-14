from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
        'npm' : '240123456',
        'name': 'Haru Urara',
        'class': 'PBP A'
    }

    return render(request, "main.html", context)