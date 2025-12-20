from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib import messages
from functools import wraps
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.html import strip_tags

from catalog.models import Product
from .models import Wishlist

def is_ajax(request):
    # helper kecil; Django <4 punya request.is_ajax() deprecated
    return request.headers.get("x-requested-with") == "XMLHttpRequest" or request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

def wishlist_list(request):
    """
    Tampilkan daftar wishlist milik user yang sedang login.
    Mendukung filter brand dan sorting via query params:
      - ?brand=<brand_name>
      - ?sort=date_desc (default), date_asc, price_desc, price_asc
    """
    if not request.user.is_authenticated:
        # user belum login -> render halaman minta login
        return render(request, "wish_list.html", {"anonymous": True})

    # ambil semua wishlist user, kemudian apply filter / sort sesuai query params
    qs = Wishlist.objects.filter(user=request.user).select_related("product")

    # available brands (hanya brand yang ada di wishlist user) untuk opsi filter
    brand_qs = Product.objects.filter(in_wishlists__user=request.user).order_by().values_list("brand", flat=True).distinct()
    # normalisasi: buang None/empty
    brands = [b for b in brand_qs if b]

    # baca parameter GET
    selected_brand = request.GET.get("brand", "").strip()
    sort = request.GET.get("sort", "date_desc").strip()

    # filter by brand jika ada
    if selected_brand:
        qs = qs.filter(product__brand=selected_brand)

    # sorting
    if sort == "date_asc":
        qs = qs.order_by("date_added")
    elif sort == "price_asc":
        # join product and order by product.price ascending; fallback to date_added to make order deterministic
        qs = qs.order_by("product__price", "-date_added")
    elif sort == "price_desc":
        qs = qs.order_by("-product__price", "-date_added")
    else:  # default date_desc
        qs = qs.order_by("-date_added")

    wish_items = list(qs.select_related("product"))

    context = {
        "wish_items": wish_items,
        "brands": brands,
        "selected_brand": selected_brand,
        "selected_sort": sort,
    }
    return render(request, "wish_list.html", context)

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

def show_json(request):
    """
    Return JSON list of wishlist items for the currently authenticated user.
    If not authenticated, return 401.
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "login required"}, status=401)

    qs = Wishlist.objects.filter(user=request.user).select_related("product")
    data = []
    for w in qs:
        prod = w.product
        item = {
            "id": w.id,
            "product_id": prod.id if prod else None,
            "product_name": str(prod) if prod else None,
            # try to include common product fields if they exist
            "product_price": getattr(prod, "price", None),
            "product_brand": getattr(prod, "brand", None),
            "product_thumbnail": getattr(prod, "thumbnail", None),
            "date_added": w.date_added.isoformat() if getattr(w, "date_added", None) else None,
            "user_id": w.user_id,
        }
        data.append(item)

    return JsonResponse(data, safe=False)


def show_json_by_id(request, wishlist_id):
    """
    Return JSON for a single wishlist item.
    Only owner or staff can access; otherwise 403.
    """
    try:
        w = Wishlist.objects.select_related("product", "user").get(pk=wishlist_id)
    except Wishlist.DoesNotExist:
        return JsonResponse({"detail": "Not found"}, status=404)

    # izin: owner atau staff
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "login required"}, status=401)

    if w.user != request.user and not request.user.is_staff:
        return JsonResponse({"detail": "permission denied"}, status=403)

    prod = w.product
    data = {
        "id": w.id,
        "product_id": prod.id if prod else None,
        "product_name": str(prod) if prod else None,
        "product_price": getattr(prod, "price", None),
        "product_brand": getattr(prod, "brand", None),
        "product_thumbnail": getattr(prod, "thumbnail", None),
        "date_added": w.date_added.isoformat() if getattr(w, "date_added", None) else None,
        "user_id": w.user_id,
        "user_username": w.user.username if getattr(w.user, "username", None) else None,
    }

    return JsonResponse(data)

def proxy_image(request):
    image_url = request.GET.get('url')
    if not image_url:
        return HttpResponse('No URL provided', status=400)
    
    try:
        # Fetch image from external source
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Return the image with proper content type
        return HttpResponse(
            response.content,
            content_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except requests.RequestException as e:
        return HttpResponse(f'Error fetching image: {str(e)}', status=500)

# --- helper kecil untuk parsing body JSON atau form ---
def _parse_request_body(request):
    """
    Return a dict-like mapping of incoming body. Accepts either JSON body
    (Content-Type: application/json) or form-encoded POST (request.POST).
    """
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8') or '{}')
        except Exception:
            return {}
    # fallback to form-encoded
    try:
        return request.POST.dict()
    except Exception:
        return {}

@csrf_exempt
def add_to_wishlist_flutter(request):
    # Hanya POST
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=400)

    # Periksa autentikasi (Flutter harus kirim cookie/session atau token)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)

    data = _parse_request_body(request)

    product_id = data.get("product_id")
    if product_id is None:
        return JsonResponse({"error": "product_id is required"}, status=400)

    try:
        product_id = int(product_id)
    except (ValueError, TypeError):
        return JsonResponse({"error": "invalid product_id"}, status=400)

    product = get_object_or_404(Product, pk=product_id)

    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    status_code = 201 if created else 200
    return JsonResponse({
        "created": created,
        "product_id": product_id,
        "message": "Added to wishlist" if created else "Already in wishlist"
    }, status=status_code)

@csrf_exempt
def remove_from_wishlist_flutter(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed."}, status=400)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "login required"}, status=401)

    data = _parse_request_body(request)

    wishlist_id = data.get("wishlist_id")
    product_id = data.get("product_id")

    # Prioritaskan wishlist_id jika disediakan
    if wishlist_id is not None:
        try:
            wishlist_id = int(wishlist_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "invalid wishlist_id"}, status=400)

        wish_item = get_object_or_404(Wishlist, pk=wishlist_id)

        # izin: pemilik atau staff
        if wish_item.user != request.user and not request.user.is_staff:
            return JsonResponse({"error": "permission denied"}, status=403)

        wish_item.delete()
        return JsonResponse({"deleted": True, "wishlist_id": wishlist_id}, status=200)

    # Jika product_id diberikan, cari item wishlist milik user untuk product tersebut
    if product_id is not None:
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "invalid product_id"}, status=400)

        product = get_object_or_404(Product, pk=product_id)
        wish_item = Wishlist.objects.filter(user=request.user, product=product).first()
        if not wish_item:
            return JsonResponse({"deleted": False, "message": "not found"}, status=404)

        wish_item.delete()
        return JsonResponse({"deleted": True, "product_id": product_id}, status=200)

    return JsonResponse({"error": "wishlist_id or product_id required"}, status=400)

@csrf_exempt
def toggle_wishlist_flutter(request):
    # 1. Cek Method
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed."}, status=400)

    # 2. Cek Autentikasi
    # Pastikan user sudah login via Flutter
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Login required"}, status=401)

    # 3. Parse Body
    data = _parse_request_body(request)

    product_id = data.get("product_id")
    if product_id is None:
        return JsonResponse({"status": "error", "message": "product_id is required"}, status=400)

    # 4. Validasi Product ID (Integer)
    try:
        product_id = int(product_id)
    except (ValueError, TypeError):
        return JsonResponse({"status": "error", "message": "Invalid product_id format"}, status=400)

    # 5. Cari Product (Gunakan try-except alih-alih get_object_or_404)
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # PENTING: Return JSON error, jangan HTML error
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    # 6. Logic Toggle
    # Menggunakan filter().first() lebih aman daripada get() untuk menghindari MultipleObjectsReturned
    existing_wishlist = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if existing_wishlist:
        existing_wishlist.delete()
        status = "removed"
    else:
        Wishlist.objects.create(user=request.user, product=product)
        status = "added"

    return JsonResponse({
        "status": status, 
        "product_id": product_id,
        "message": "Success"
    }, status=200)