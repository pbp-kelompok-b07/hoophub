from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django import forms
from django.http import JsonResponse

# ---------- FORM ----------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['rating']


# ---------- VIEW: LIST + FILTER ----------
def product_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category=category)
    if brand:
        products = products.filter(brand__icontains=brand)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    return render(request, 'catalog/product_list.html', {'products': products})


# ---------- VIEW: DETAIL ----------
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'p': product})


# ---------- VIEW: CREATE (untuk AJAX modal) ----------
def product_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        brand = request.POST.get("brand")
        category = request.POST.get("category")
        description = request.POST.get("description") 
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        image = request.POST.get("image")
        release_date = request.POST.get("release_date")
        is_available = request.POST.get("is_available") == "on"

        Product.objects.create(
            name=name,
            brand=brand,
            category=category,
            description=description,
            price=price,
            stock=stock,
            image=image,
            release_date=release_date,
            is_available=is_available,
        )
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


# ---------- VIEW: UPDATE ----------
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


# ---------- VIEW: DELETE ----------
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


# ---------- VIEW: JSON (untuk grid di frontend) ----------
def products_json(request):
    products = Product.objects.filter(is_available=True).values(
        "id", "name", "brand", "category", "price",
        "release_date", "is_available", "image", "description"
    )
    data = list(products)
    return JsonResponse(data, safe=False)

