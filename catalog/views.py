from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django import forms
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product
import json
# ---------- FORM ----------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['rating']
@csrf_exempt
def edit_product(request, id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid method"}, status=405)

    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse(
            {"success": False, "message": "Unauthorized"},
            status=403
        )

    product = get_object_or_404(Product, id=id)

    try:
        product.name = request.POST.get("name", product.name)
        product.brand = request.POST.get("brand", product.brand)
        product.category = request.POST.get("category", product.category)
        product.description = request.POST.get("description", product.description)
        product.price = int(request.POST.get("price", product.price))
        product.stock = int(request.POST.get("stock", product.stock))
        product.image = request.POST.get("image", product.image)
        product.save()
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": str(e)},
            status=400
        )

    return JsonResponse({"success": True})

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
@csrf_exempt
def product_create(request):
    if request.method == "POST":

        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse(
                {"success": False, "message": "Unauthorized"},
                status=403
            )

        try:
            Product.objects.create(
                name=request.POST.get("name"),
                brand=request.POST.get("brand"),
                category=request.POST.get("category"),
                description=request.POST.get("description"),
                price=int(request.POST.get("price", 0)),
                stock=int(request.POST.get("stock", 0)),
                image=request.POST.get("image"),
                release_date=request.POST.get("release_date") or None,
                is_available=request.POST.get("is_available") == "on",
            )
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": str(e)},
                status=400
            )

        return JsonResponse({"success": True})

    return JsonResponse(
        {"success": False, "message": "Invalid request"},
        status=400
    )


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
        "release_date", "is_available", "image", "description","stock",
    )
    return JsonResponse(list(products), safe=False)

def get_reviews(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    
    data = [
        {
            'id': str(review.id),
            'user': review.user.username,
            'rating': review.rating,
            'review': review.review,
            'date': review.date.strftime('%d %B %Y')
        }
        for review in reviews
    ]
    return JsonResponse(data, safe=False)

def products_filtered_json(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    brand = request.GET.get('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.filter(is_available=True)

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

    data = list(products.values(
        "id",
        "name",
        "brand",
        "category",
        "price",
        "release_date",
        "is_available",
        "image",
        "description",
        "stock",
    ))
    return JsonResponse(data, safe=False)
@csrf_exempt
def edit_product_flutter(request, id):
    if request.method == 'POST':
        try:
            product = Product.objects.get(pk=id)
            
            data = json.loads(request.body)
            
            product.name = data['name']
            product.brand = data['brand']
            product.category = data['category']
            product.description = data['description']
            product.price = int(data['price'])
            product.stock = int(data['stock'])
            product.image_url = data['image_url'] 
            
            product.save()
            
            return JsonResponse({"status": "success"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Produk tidak ditemukan"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)
@csrf_exempt
def create_product_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            new_product = Product.objects.create(
                user=request.user, 
                name=data["name"],
                brand=data["brand"],
                category=data["category"],
                price=int(data["price"]),
                stock=int(data["stock"]),
                description=data["description"],
                image=data["image"], 
            )
            new_product.save()

            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)
@csrf_exempt
def create_product_flutter(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"status": "error", "message": "Harus login terlebih dahulu"}, status=403)

            data = json.loads(request.body)
            
            new_product = Product.objects.create(
                name=data["name"],
                brand=data["brand"],
                category=data["category"],
                price=int(data["price"]),
                stock=int(data["stock"]),
                description=data["description"],
                image=data["image"],
                is_available=data["is_available"]
            )

            new_product.save()

            return JsonResponse({"status": "success"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)
@csrf_exempt
def delete_product_flutter(request, id):
    if request.method == 'POST':
        try:
            # Pastikan hanya Admin yang bisa menghapus
            if not request.user.is_superuser: # Atau is_staff, sesuaikan logic kamu
                 return JsonResponse({"status": "error", "message": "Bukan Admin"}, status=403)

            product = Product.objects.get(pk=id)
            product.delete()
            return JsonResponse({"status": "success"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Produk tidak ditemukan"}, status=404)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)