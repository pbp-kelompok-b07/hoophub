from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django import forms
from django.http import JsonResponse


# form untuk CRUD
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
def product_view(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')

    products = Product.objects.filter(is_available=True)

    if query:
        products = products.filter(name__icontains=query)
    if category:
        products = products.filter(category=category)
    if brand:
        products = products.filter(brand__icontains=brand)

    return render(request, 'catalog/product_view.html', {'products': products})

# view list + filter
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

# view create
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_form.html', {'form': form})

# view update
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_form.html', {'form': form, 'product': product})

# view delete
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('catalog:product_list')
    return render(request, 'catalog/product_delete.html', {'product': product})
# === endpoint JSON untuk AJAX ===
def products_json(request):
    products = Product.objects.filter(is_available=True).values(
        "id", "name", "brand", "category", "price", "rating",
        "release_date", "is_available", "image"
    )
    data = list(products)
    return JsonResponse(data, safe=False)