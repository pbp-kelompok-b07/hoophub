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

@login_required
def get_cart_json(request):
    cart_items = Product.objects.filter(user=request.user)
    
    data = []
    
    for item in cart_items:
        img_url = ""
        if item.product.image:
            img_url = item.product.image.url
            
        data.append({
            "model": "cart.cartitem",
            "pk": item.pk,
            "fields": {
                "user": item.user.id,
                "product": item.product.id,
                
                "product_name": item.product.name,
                "price": int(item.product.price),
                "quantity": item.quantity,
                "thumbnail_url": img_url,
                
                "subtotal": int(item.product.price * item.quantity)
            }
        })
    
    return JsonResponse(data, safe=False)

import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from catalog.models import Product

@csrf_exempt
@require_POST
def add_to_cart_flutter(request, product_id):
    if request.method == 'POST':
        try:
            user = request.user
            
            catalog_product = Product.objects.get(pk=product_id)
            
            cart_item = Product.objects.filter(user=user, name=catalog_product.name).first()

            if cart_item:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({"status": "success", "message": "Jumlah produk ditambahkan"}, status=200)
            else:
                new_item = Product(
                    user=user,
                    name=catalog_product.name,
                    price=catalog_product.price,
                    description=catalog_product.description,
                    quantity=1,
                    image=catalog_product.image, 
                    brand=catalog_product.brand,
                    stock=catalog_product.stock 
                )
                new_item.save()
                return JsonResponse({"status": "success", "message": "Produk berhasil ditambahkan ke keranjang"}, status=200)

        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Produk tidak ditemukan"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=401)

@csrf_exempt
def delete_cart_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get("id")
            
            item = Product.objects.get(pk=item_id)
            item.delete()
            
            return JsonResponse({"status": "success"}, status=200)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Item not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=401)

@csrf_exempt
def checkout_flutter(request):
    if request.method == 'POST':
        user = request.user
        cart_items = Product.objects.filter(user=user)
        
        if not cart_items.exists():
             return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)
        
        cart_items.delete()
        
        return JsonResponse({"status": "success", "message": "Checkout successful!"}, status=200)
        
    return JsonResponse({"status": "error"}, status=401)