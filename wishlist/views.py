from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.urls import reverse
from django.contrib import messages
from functools import wraps

from catalog.models import Product
from .models import Wishlist

def is_ajax(request):
    # helper kecil; Django <4 punya request.is_ajax() deprecated
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

def wishlist_list(request):
    """
    Tampilkan daftar wishlist milik user yang sedang login.
    """
    if not request.user.is_authenticated:
        # user belum login -> render halaman minta login
        return render(request, "wish_list.html", {"anonymous": True})
    # user sudah login -> ambil dan render wishlist
    wish_items = Wishlist.objects.filter(user=request.user).select_related("product").order_by("-date_added")
    return render(request, "wish_list.html", {"wish_items": wish_items})

@login_required
def add_to_wishlist(request, product_id):
    """
    Tambah product ke wishlist user. Hanya POST.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    product = get_object_or_404(Product, pk=product_id)

    # buat / ambil wishlist item
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if is_ajax(request):
        status_code = 201 if created else 200
        return JsonResponse({
            "created": created,
            "product_id": product_id,
            "message": "Added to wishlist" if created else "Already in wishlist"
        }, status=status_code)

    # non-AJAX fallback
    if created:
        messages.success(request, f"'{product}' ditambahkan ke wishlist.")
    else:
        messages.info(request, f"'{product}' sudah ada di wishlist kamu.")

    next_url = request.POST.get("next") or request.GET.get("next") or reverse("wishlist:list")
    return redirect(next_url)

@login_required
def remove_from_wishlist(request, pk):
    """
    Hapus item wishlist berdasarkan primary key Wishlist. Hanya POST.
    Admin (is_staff) boleh menghapus item siapa pun; user biasa hanya item sendiri.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    wish_item = get_object_or_404(Wishlist, pk=pk)

    # izin: pemilik atau admin/staff
    if wish_item.user != request.user and not request.user.is_staff:
        # untuk AJAX: kirim 403 JSON; non-AJAX: HttpResponseForbidden
        if is_ajax(request):
            return JsonResponse({"error": "permission denied"}, status=403)
        return HttpResponseForbidden("You don't have permission to remove this item.")

    wish_item.delete()

    if is_ajax(request):
        return JsonResponse({"deleted": True, "wishlist_id": pk}, status=200)

    messages.success(request, "Item dihapus dari wishlist.")
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("wishlist:list")
    return redirect(next_url)

def ajax_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'error': 'login required'}, status=401)
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return view_func(request, *args, **kwargs)
    return _wrapped

@login_required
def toggle_wishlist(request, product_id):
    """
    Toggle via POST: jika ada -> hapus, jika belum -> tambah.
    Mengembalikan JSON (ideal untuk tombol heart via AJAX).
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST allowed.")

    product = get_object_or_404(Product, pk=product_id)

    existing = Wishlist.objects.filter(user=request.user, product=product).first()
    if existing:
        existing.delete()
        status = "removed"
    else:
        Wishlist.objects.create(user=request.user, product=product)
        status = "added"

    return JsonResponse({"status": status, "product_id": product_id}, status=200)