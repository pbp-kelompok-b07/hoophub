import datetime
import json
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from invoice.models import Invoice
from invoice.forms import InvoiceForm
from cart.models import Order, OrderItem, CartItem  # penting: ambil model Order karena Invoice punya foreign key ke Order
from catalog.models import Product

ALLOWED_STATUSES = {"Pending", "Paid", "Shipped", "Cancelled"}

@login_required(login_url='/authenticate/login')
@require_http_methods(["GET", "POST"])
def reorder_invoice(request, id):
    inv = get_object_or_404(Invoice, pk=id, user=request.user)
    order = inv.order

    if request.method == "GET":
        first = order.items.select_related("product").first() if order else None
        if not first:
            return JsonResponse({"status": "error", "message": "Produk tidak tersedia."}, status=400)
        p = first.product
        img = ((getattr(p, "image", None) and getattr(p.image, "url", "")) or getattr(p, "thumbnail", ""))
        return JsonResponse({
            "status": "success",
            "product_id": p.id,
            "name": getattr(p, "name", ""),
            "brand": getattr(p, "brand", ""),
            "price": getattr(p, "price", 0),
            "image": img,
        })

    cart = request.session.get("cart", {})
    if order:
        for it in order.items.select_related("product"):
            pid = str(it.product_id)
            if pid in cart:
                cart[pid]["quantity"] = cart[pid].get("quantity", 0) + it.quantity
            else:
                cart[pid] = {"quantity": it.quantity}

    request.session["cart"] = cart
    request.session.modified = True
    redirect_url = reverse("cart:show_cart") + "?checkout=1"
    return JsonResponse({"status": "success", "redirect_url": redirect_url})


@login_required(login_url='/authenticate/login')
@require_POST
def delete_invoice(request, id):
    inv = get_object_or_404(Invoice, pk=id, user=request.user)
    inv.delete()
    return JsonResponse({"status": "success"})


def generate_invoice_no(user_id: int) -> str:
    now = datetime.datetime.now()
    return f"INV{now:%Y%m%d}-{user_id}-{now:%H%M%S}"


def show_invoices(request):
    if request.user.is_authenticated:
        invoices = Invoice.objects.filter(user=request.user).select_related('order').order_by('-date')
        for inv in invoices:
            if inv.order:
                for item in inv.order.items.all():
                    item.subtotal = item.price_at_checkout * item.quantity

        return render(request, "invoice.html", {"invoices": invoices})
    else:
        return render(request, "invoice.html")


@login_required(login_url='/authenticate/login')
def invoice_detail(request, id):
    invoice = get_object_or_404(Invoice, pk=id, user=request.user)
    return render(request, "invoice_detail.html", {"invoice": invoice})


@login_required(login_url='/authenticate/login')
def create_invoice(request):
    invoice_created = False
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.date = timezone.now().date()
            invoice.invoice_no = generate_invoice_no(request.user.id)

            order_id = form.cleaned_data.get("order")
            if order_id:
                invoice.order = order_id
            invoice.save()

            invoice_created = True
            return redirect("invoice:invoice_detail", id=invoice.id)
    else:
        form = InvoiceForm()

    return render(request, "invoice_create.html", {
        "form": form,
        "invoice_created": invoice_created,
    })


@login_required(login_url='/authenticate/login')
def invoice_detail_json(request, id):
    invoice = get_object_or_404(Invoice, pk=id, user=request.user)
    order = invoice.order

    items = []
    if order:
        for it in order.items.select_related("product"):
            p = it.product
            img = str(getattr(p, "image", "")) or getattr(p, "thumbnail", "") or ""
            
            items.append({
                "product_id": p.id,
                "name": p.name,
                "brand": p.brand,
                "price": it.price_at_checkout,
                "quantity": it.quantity,
                "subtotal": it.price_at_checkout * it.quantity,
                "image": img,
            })

    data = {
        "invoice_no": invoice.invoice_no,
        "date": invoice.date.strftime("%Y-%m-%d"),
        "order_id": str(order.id) if order else "",
        "full_name": getattr(order, "full_name", ""),
        "address": getattr(order, "address", ""),
        "city": getattr(order, "city", ""),
        "postal_code": getattr(order, "postal_code", ""),
        "total_price": str(getattr(order, "total_price", 0)),
        "status": getattr(order, "status", "Pending"),
        "items": items,
    }
    return JsonResponse(data)

@login_required(login_url='/authenticate/login')
@require_POST
def update_status(request, id):
    invoice = get_object_or_404(Invoice, pk=id, user=request.user)
    order = invoice.order
    if not order:
        return JsonResponse({
            "status": "error",
            "message": "Order tidak ditemukan."
        }, status=400)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "message": "Body tidak valid."
        }, status=400)

    new_status = data.get("status")

    if new_status not in ALLOWED_STATUSES:
        return JsonResponse({
            "status": "error",
            "message": "Status tidak valid."
        }, status=400)

    # update status di db
    order.status = new_status
    order.save()

    return JsonResponse({
        "status": "success",
        "new_status": new_status,
    })


@csrf_exempt
def show_invoice_json_flutter(request):
    # 1. Cek Autentikasi
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Must be logged in"},
            status=401
        )

    # 2. Cek status admin (untuk fleksibilitas)
    is_admin = request.user.is_superuser or 'admin' in request.user.username.lower()

    # 3. Filter query: 
    # Jika admin ingin melihat semua, gunakan .all(). 
    # Jika hanya ingin milik sendiri (sesuai permintaanmu), gunakan filter(user=request.user)
    if is_admin:
        # Opsional: ganti jadi .filter(user=request.user) jika admin tetap hanya lihat miliknya
        invoices = Invoice.objects.all() 
    else:
        invoices = Invoice.objects.filter(user=request.user)

    # Optimalisasi Query
    invoices = invoices.select_related('order')\
                       .prefetch_related('order__items__product')\
                       .order_by('-date')

    invoices_data = []

    # 4. Loop Susun Data
    for invoice in invoices:
        order = invoice.order
        items_list = []

        if order:
            for it in order.items.all():
                p = it.product
                # Logika ambil gambar
                img = ""
                if hasattr(p, "image") and p.image:
                    img = str(p.image)
                elif hasattr(p, "thumbnail") and p.thumbnail:
                    img = str(p.thumbnail)

                items_list.append({
                    "product_id": p.id,
                    "name": p.name,
                    "brand": getattr(p, "brand", ""),
                    "price": float(it.price_at_checkout),
                    "quantity": it.quantity,
                    "subtotal": float(it.price_at_checkout * it.quantity),
                    "image": img,
                })

        # Data per satu Invoice
        invoices_data.append({
            "id": invoice.id,
            "invoice_no": invoice.invoice_no,
            "date": invoice.date.strftime("%Y-%m-%d %H:%M"),
            "full_name": getattr(order, "full_name", ""),
            "address": getattr(order, "address", ""),
            "city": getattr(order, "city", ""),
            "total_price": float(getattr(order, "total_price", 0)),
            "status": getattr(order, "status", "Pending"),
            "items": items_list,
        })

    # 5. Return Dictionary (Lebih aman dan rapi untuk Flutter)
    return JsonResponse({
        "status": "success",
        "is_admin": is_admin,
        "invoices": invoices_data
    })

@csrf_exempt
def create_invoice_flutter(request):
    # Cek auth secara manual agar return JSON, bukan Redirect HTML
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "User not authenticated"}, status=401)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Ambil data utama dari JSON Flutter
            full_name = data.get("fullName")
            address = data.get("address")
            city = data.get("city")
            total_price = data.get("totalPrice", 0)
            
            # VALIDASI: Pastikan ada barang yang dibeli
            items_data = data.get("items", [])
            if not items_data:
                return JsonResponse({"status": "error", "message": "Cart is empty"}, status=400)

            # 1. Mulai proses pembuatan Invoice
            # Jika model Invoice kamu hanya bisa simpan SATU produk (seperti di kodenya):
            first_item = items_data[0]
            product_id = first_item.get("productId")
            product_instance = get_object_or_404(Product, pk=product_id)

            new_invoice = Invoice.objects.create(
                user=request.user,
                invoice_no=generate_invoice_no(request.user.id), # Pastikan fungsi ini ada
                full_name=full_name,
                product=product_instance, # Jika model Invoice punya field product
                address=address,
                city=city,
                total_price=int(total_price),
                status="Pending",
            )

            # 2. Hapus Cart HANYA JIKA Invoice berhasil dibuat
            CartItem.objects.filter(user=request.user).delete()

            return JsonResponse({
                "status": "success",
                "message": "Invoice created and cart cleared!"
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=400)
            
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)