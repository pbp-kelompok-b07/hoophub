import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from invoice.models import Invoice

# Create your views here.

# @login_required(login_url='/authenticate/login')
def show_invoices(request):
    # invoices = Invoice.objects.filter(user=request.user)
    return render(request, "invoice.html", None)#{"invoices" : invoices})

@login_required(login_url='/authenticate/login')
def invoice_detail(request, id):
    invoice = get_object_or_404(Invoice, pk=id)
    return render(request, "invoice_detail.html", {"invoice" : invoice})
