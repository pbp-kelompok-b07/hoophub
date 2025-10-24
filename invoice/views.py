import datetime
import json
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from invoice.models import Invoice
from invoice.forms import InvoiceForm
from cart.models import Order, OrderItem  # penting: ambil model Order karena Invoice punya foreign key ke Order
from catalog.models import Product

ALLOWED_STATUSES = {"Pending", "Paid", "Shipped", "Cancelled"}

@login_required(login_url='/authenticate/login')
@require_http_methods(["GET", "POST"])
def reorder_invoice(request, id):
    inv = get_object_or_404(Invoice, pk=id, user=request.user)
    order = inv.order

    if request.method == "GET":
        # modal preview: pakai item pertama saja untuk ringkasan
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

    # POST -> masukkan SEMUA item order ke cart
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
    """
    Hapus invoice milik user, dipanggil dari modal konfirmasi.
    """
    inv = get_object_or_404(Invoice, pk=id, user=request.user)
    inv.delete()
    return JsonResponse({"status": "success"})


# --- Utility untuk generate nomor invoice ---
def generate_invoice_no(user_id: int) -> str:
    now = datetime.datetime.now()
    return f"INV{now:%Y%m%d}-{user_id}-{now:%H%M%S}"


# --- Tampilkan semua invoice milik user login ---
def show_invoices(request):
    invoices = Invoice.objects.filter(user=request.user).select_related('order').order_by('-date')
    for inv in invoices:
        if inv.order:
            for item in inv.order.items.all():
                item.subtotal = item.price_at_checkout * item.quantity

    return render(request, "invoice.html", {"invoices": invoices})


# --- Tampilkan detail satu invoice ---
@login_required(login_url='/authenticate/login')
def invoice_detail(request, id):
    invoice = get_object_or_404(Invoice, pk=id, user=request.user)
    return render(request, "invoice_detail.html", {"invoice": invoice})


# --- Buat invoice baru berdasarkan Order yang sudah ada ---
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

            # Ambil order dari form (misal ada field 'order' di InvoiceForm)
            order_id = form.cleaned_data.get("order")
            if order_id:
                invoice.order = order_id  # kalau form-nya pakai ModelChoiceField ke Order
            invoice.save()

            invoice_created = True
            return redirect("invoice:invoice_detail", id=invoice.id)
    else:
        form = InvoiceForm()

    return render(request, "invoice_create.html", {
        "form": form,
        "invoice_created": invoice_created,
    })


# --- Endpoint JSON untuk detail invoice (ambil data dari order) ---
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
    """
    Ubah status order yg terkait invoice[id] milik user saat ini.
    Body: {"status": "Paid"}
    """
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


