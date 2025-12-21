from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from report.forms import ReportForm
from report.models import Report
from review.models import Review
from catalog.models import Product
from django.contrib.auth.decorators import user_passes_test
import requests

# Create your views here.
LOGIN_URL = '/authentication/login/'

def show_report(request):
    if request.user.is_authenticated:
        if request.user.username.lower() == 'admin':
            report_list = Report.objects.all()
        else:
            report_list = Report.objects.filter(reporter=request.user)
        context = {
            'report_list': report_list,
            'last_login': request.COOKIES.get('last_login', 'Never')
        }
        return render(request, 'report.html', context)
    else:
        return render(request, 'report.html')


@login_required(login_url=LOGIN_URL)
def create_report_ajax(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        report_type = request.POST.get('report_type')
        object_id = request.POST.get('object_id')

        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.report_type = report_type

            if report_type == 'product':
                report.reported_product = get_object_or_404(Product, pk=object_id)
            elif report_type == 'review':
                report.reported_review = get_object_or_404(Review, pk=object_id)
            
            report.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required(login_url=LOGIN_URL)
@csrf_exempt
def edit_report(request, id):
    report = get_object_or_404(Report, id=id, reporter=request.user)

    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": "Report successfully updated."
            })
        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@login_required(login_url=LOGIN_URL)
@csrf_exempt
def delete_report(request, id):
    if request.method == "POST":
        try:
            if request.user.username.lower() == 'admin':
                report = get_object_or_404(Report, pk=id)
            else:
                report = get_object_or_404(Report, pk=id, reporter=request.user)
            
            report.delete()
            return JsonResponse({"success": True})
        except Exception as e:
            print(f"[DEBUG] Delete error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

@login_required(login_url=LOGIN_URL)
def report_detail(request, id):
    if request.user.username.lower() == 'admin':
        # Admin bisa lihat semua report
        report = get_object_or_404(Report, id=id)
    else:
        # User biasa hanya bisa lihat report miliknya sendiri
        report = get_object_or_404(Report, id=id, reporter=request.user)

    # Kalau admin update status
    if request.method == "POST":
        new_status = request.POST.get("status")
        if request.user.username.lower() == 'admin' and new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to {report.get_status_display()}!")

    context = {
        "report": report,
        "last_login": request.COOKIES.get("last_login", "Never"),
    }

    return render(request, "report_detail.html", context)


def is_admin(user):
    return user.username.lower() == 'admin'

@user_passes_test(is_admin)
def admin_report_list(request):
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'admin_report_list.html', {'report_list': reports})

@user_passes_test(is_admin)
def admin_report_detail(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ['pending', 'resolved', 'rejected']:
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to {new_status.title()}.")
            return redirect('report:admin_report_detail', report_id=report.id)
        else:
            messages.error(request, "Invalid status selected.")

    return render(request, 'admin_report_detail.html', {'report': report})

@csrf_exempt
def show_json_flutter(request):
    # Optimasi query
    reports = Report.objects.select_related("reporter", "reported_user", "reported_product")
    data = []
    for r in reports:
        data.append({
            "id": str(r.id),
            "report_type": r.report_type,
            "status": r.status,
            "title": r.title,
            "description": r.description,
            "created_at": r.created_at.strftime("%d %B %Y"),
            "updated_at": r.updated_at.strftime("%d %B %Y"),

            # Reporter (yang membuat report)
            "reporter": {
                "id": r.reporter.id,
                "username": r.reporter.username,
            },

            # User yang dilaporkan
            "reported_user": {
                "id": r.reported_user.id if r.reported_user else None,
                "username": r.reported_user.username if r.reported_user else None,
            },

            # Produk yang dilaporkan
            "reported_product": {
                "id": r.reported_product.id if r.reported_product else None,
                "name": r.reported_product.name if r.reported_product else None,
                "price": r.reported_product.price if r.reported_product else None,
                "image": r.reported_product.image if r.reported_product else None,
            },
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def show_my_json_flutter(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {"status": "error", "message": "Must be logged in"},
            status=401
        )

    # 1. Cek status admin simpan di variabel
    is_admin = request.user.is_superuser or 'admin' in request.user.username.lower()

    # 2. Filter query
    if is_admin:
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(reporter=request.user)

    reports = reports.select_related(
        "reporter", "reported_user", "reported_product"
    )

    # 3. Buat List Report
    reports_data = [
        {
            "id": str(r.id),
            "report_type": r.report_type,
            "status": r.status,
            "title": r.title,
            "description": r.description,
            "created_at": r.created_at.strftime("%d %B %Y"),
            "updated_at": r.updated_at.strftime("%d %B %Y"),
            "reporter": {
                "id": r.reporter.id,
                "username": r.reporter.username,
            },
            "reported_user": (
                {
                    "id": r.reported_user.id,
                    "username": r.reported_user.username,
                } if r.reported_user else None
            ),
            "reported_product": (
                {
                    "id": r.reported_product.id,
                    "name": r.reported_product.name,
                    "price": r.reported_product.price,
                    "image": r.reported_product.image if r.reported_product.image else None
                } if r.reported_product else None
            ),
        }
        for r in reports
    ]

    # 4. Return Dictionary (bukan List langsung)
    return JsonResponse({
        "status": "success",
        "is_admin": is_admin,  # <--- Ini kuncinya!
        "reports": reports_data # Data list masuk ke sini
    }) # safe=False tidak perlu jika luarnya dictionary

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
        
@csrf_exempt
@login_required(login_url=LOGIN_URL)
def create_report_flutter(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        report_type = request.POST.get('report_type')
        object_id = request.POST.get('object_id')

        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.report_type = report_type

            if report_type == 'product':
                report.reported_product = get_object_or_404(Product, pk=object_id)
            elif report_type == 'review':
                report.reported_review = get_object_or_404(Review, pk=object_id)
            
            report.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

from django.shortcuts import get_object_or_404

@csrf_exempt
def edit_report_flutter(request, id):
    if request.method == 'POST':
        # 1. Cari report berdasarkan ID
        report = get_object_or_404(Report, pk=id)

        # 2. Validasi Keamanan: 
        if report.reporter != request.user and not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Anda tidak memiliki izin mengedit report ini.'}, status=403)

        # 3. Ambil data dari request
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        status = request.POST.get('status') 

        # 4. Validasi input tidak kosong
        if title and description:
            report.title = title
            report.description = description
            
            if request.user.is_superuser and status:
                report.status = status

            report.save()

            return JsonResponse({'status': 'success', 'message': 'Report berhasil diperbarui'})
        
        return JsonResponse({'status': 'error', 'message': 'Title dan Description tidak boleh kosong'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def delete_report_flutter(request, id):
    # Hanya menerima method POST agar tidak terhapus tidak sengaja lewat browser
    if request.method == 'POST':
        # 1. Cari report berdasarkan ID
        report = get_object_or_404(Report, pk=id)

        # 2. Validasi Keamanan:
        # Cek apakah user adalah pemilik report ATAU user adalah admin
        if report.reporter != request.user and not request.user.is_superuser:
            return JsonResponse({
                'status': 'error', 
                'message': 'Anda tidak memiliki izin menghapus report ini.'
            }, status=403)

        # 3. Hapus data
        report.delete()
        

        return JsonResponse({'status': 'success', 'message': 'Report berhasil dihapus'})

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def change_status_flutter(request, report_id):
    if request.method == 'POST':
        try:
            report = Report.objects.get(pk=report_id)
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status:
                report.status = new_status
                report.save()
                return JsonResponse({"status": "success", "message": "Status updated"})
            else:
                return JsonResponse({"status": "error", "message": "No status provided"}, status=400)
        except Report.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Report not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

