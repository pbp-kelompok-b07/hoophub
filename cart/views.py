from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from catalog.models import Product 
from invoice.models import Invoice
from cart.models import Order, OrderItem
import datetime
from django.views.decorators.csrf import csrf_exempt
import json

def show_cart(request):
    cart_data = request.session.get('cart', {})
    
    cart_items = []
    total_cart_price = 0
    
    for product_id, item_data in cart_data.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data.get('quantity', 1) 
            item_total = product.price * quantity
            total_cart_price += item_total
            
            cart_items.append({
                'product': product,
                'id': product_id,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            if product_id in request.session.get('cart', {}):
                del request.session['cart'][product_id]
                request.session.modified = True
            continue
            
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price,
    }
    
    return render(request, 'cart.html', context)


@login_required(login_url="authentication:login")
def show_checkout(request):
    if request.method == 'POST':
        cart_data = request.session.get('cart', {})
        if not cart_data:
            return JsonResponse({'status': 'error', 'message': 'Keranjang Anda kosong.'}, status=400)

        # Hitung total dan siapkan data cart
        cart_items = []
        total_cart_price = 0
        for product_id, item_data in cart_data.items():
            try:
                product = Product.objects.get(id=product_id)
                quantity = item_data.get('quantity', 1)
                item_total = product.price * quantity
                total_cart_price += item_total
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price_at_checkout': product.price, 
                })
            except Product.DoesNotExist:
                continue

        # Ambil data form dari checkout
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

                # 2) Buat OrderItem untuk setiap item di keranjang
                for ci in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=ci["product"],
                        quantity=ci["quantity"],
                        price_at_checkout=ci["price_at_checkout"],
                    )

                # 3) Buat Invoice yang mengacu ke Order
                timestamp = int(datetime.datetime.now().timestamp())
                invoice_no = f"INV-{request.user.id}-{timestamp}"

                first_item = cart_items[0] if cart_items else None
                product = first_item["product"] if first_item else None  # sementara tetap isi

                invoice = Invoice.objects.create(
                    user=request.user,
                    product=product,  # bisa dihapus di masa depan jika sudah full multi-item
                    date=datetime.datetime.now().date(),
                    invoice_no=invoice_no,
                    order=order
                )

            # 4) Hapus cart session
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

            # 5) Redirect ke halaman invoice detail
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
    cart = request.session.get('cart', {})
    product_id_str = str(id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
    return HttpResponseRedirect(reverse('cart:show_cart'))

@login_required(login_url="authentication:login")
@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}
    request.session['cart'] = cart
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'main:show_main'))

def get_cart_json(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User belum login"}, status=401)
    cart = request.session.get('cart', {})
    data = []

    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data.get('quantity', 1)
            subtotal = product.price * quantity
            
            data.append({
                "pk": product.id,
                "fields": {
                    "product_name": product.name,
                    "price": product.price,
                    "quantity": quantity,
                    "subtotal": subtotal,
                    "thumbnail_url": product.image.url if product.image else "",
                }
            })
        except Product.DoesNotExist:
            continue

    return JsonResponse(data, safe=False)

@csrf_exempt
def add_to_cart_flutter(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({"status": "error", "message": "Produk tidak ditemukan"}, status=404)

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {'quantity': 1}
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({"status": "success", "message": "Berhasil ditambahkan ke keranjang"}, status=200)

    return JsonResponse({"status": "error", "message": "Invalid method"}, status=401)

@csrf_exempt
def delete_cart_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = str(data.get("id"))
        
        cart = request.session.get('cart', {})
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({"status": "success", "message": "Item dihapus"}, status=200)
        
        return JsonResponse({"status": "error", "message": "Item tidak ada di keranjang"}, status=404)
        
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def checkout_flutter(request):
    if request.method == 'POST':
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True
            return JsonResponse({"status": "success", "message": "Checkout successful!"}, status=200)
        else:
            return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)
        
    return JsonResponse({"status": "error"}, status=401)