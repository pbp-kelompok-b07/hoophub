from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from catalog.models import Product 
from invoice.models import Invoice
from cart.models import Order, OrderItem, CartItem # Pastikan CartItem sudah diimport
import datetime
import json

@login_required(login_url="authentication:login")
def show_cart(request):
    # Mengambil data dari DATABASE (Sinkron)
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Hitung total harga
    total_cart_price = sum(item.subtotal for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    
    return render(request, 'cart.html', context)

@login_required(login_url="authentication:login")
def show_checkout(request):
    if request.method == 'POST':
        # Ambil item dari Database
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return JsonResponse({'status': 'error', 'message': 'Keranjang Anda kosong.'}, status=400)

        full_name = request.POST.get('full_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        if not all([full_name, address, city, postal_code]):
            return JsonResponse({
                'status': 'error', 
                'message': 'Semua field alamat wajib diisi!'
            }, status=400)

        try:
            with transaction.atomic():
                total_cart_price = sum(item.subtotal for item in cart_items)

                # 1) Buat Order
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    total_price=total_cart_price,
                    status="Pending"
                )

                # 2) Buat OrderItem dari CartItem database
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_at_checkout=item.product.price,
                    )

                # 3) Buat Invoice
                timestamp = int(datetime.datetime.now().timestamp())
                invoice_no = f"INV-{request.user.id}-{timestamp}"
                
                # Ambil produk pertama untuk referensi (opsional sesuai model lama)
                first_product = cart_items.first().product if cart_items.exists() else None

                Invoice.objects.create(
                    user=request.user,
                    product=first_product, 
                    date=datetime.datetime.now().date(),
                    invoice_no=invoice_no,
                    order=order
                )

                # 4) HAPUS CART DARI DATABASE (Agar kosong setelah checkout)
                cart_items.delete()

            # 5) Redirect
            redirect_url = reverse('invoice:show_invoices')
            return JsonResponse({
                'status': 'success',
                'message': 'Checkout berhasil!',
                'redirect_url': redirect_url
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Terjadi kesalahan server: {e}'
            }, status=500)
    else:
        return redirect('cart:show_cart')

@login_required(login_url="authentication:login")
@require_POST
def remove_from_cart(request, id):
    # Menghapus item dari Database berdasarkan Product ID dan User
    CartItem.objects.filter(user=request.user, product_id=id).delete()
    return HttpResponseRedirect(reverse('cart:show_cart'))

@login_required(login_url="authentication:login")
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    # Cek atau buat item di database
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    # Jika barang sudah ada, update quantity-nya
    if not created:
        cart_item.quantity += quantity
        cart_item.save() # Simpan perubahan ke DB
        
    return redirect(request.META.get('HTTP_REFERER', 'main:show_main'))

def get_cart_json(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User belum login"}, status=401)
    
    # Ambil dari Database
    cart_items = CartItem.objects.filter(user=request.user)
    data = []

    for item in cart_items:
        data.append({
            "pk": item.product.id,
            "fields": {
                "product_name": item.product.name,
                "brand": item.product.brand,
                "price": item.product.price,
                "quantity": item.quantity,
                "subtotal": item.subtotal, # Menggunakan properti @property dari model
                "thumbnail_url": item.product.image if item.product.image else "",
            }
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def add_to_cart_flutter(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Simpan ke Database
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({"status": "success", "message": "Berhasil ditambahkan ke keranjang"}, status=200)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)

@csrf_exempt
def delete_cart_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)

    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get("id")
        
        # Hapus dari Database
        deleted, _ = CartItem.objects.filter(user=request.user, product_id=product_id).delete()
        
        if deleted > 0:
            return JsonResponse({"status": "success", "message": "Item dihapus"}, status=200)
        
        return JsonResponse({"status": "error", "message": "Item tidak ada di keranjang"}, status=404)
        
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def checkout_flutter(request):
    # Wajib login untuk akses database cart
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)

    if request.method == 'POST':
        # Cek apakah ada item di database cart user
        cart_exists = CartItem.objects.filter(user=request.user).exists()
        
        if cart_exists:
            # HAPUS DATA DARI DATABASE (Bukan Session lagi)
            CartItem.objects.filter(user=request.user).delete()
            
            return JsonResponse({"status": "success", "message": "Checkout successful!"}, status=200)
        else:
            return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)
        
    return JsonResponse({"status": "error"}, status=401)