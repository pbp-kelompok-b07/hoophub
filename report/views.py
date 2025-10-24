from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from report.forms import ReportForm
from report.models import Report
from review.models import Review
from catalog.models import Product
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
LOGIN_URL = '/authentication/login/'

def show_report(request):
    if request.user.is_authenticated:
        if request.user.is_staff or 'admin' in request.user.username.lower():
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
            if request.user.is_staff or request.user.is_superuser:
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
    if request.user.is_staff or 'admin' in request.user.username.lower():
        # Admin bisa lihat semua report
        report = get_object_or_404(Report, id=id)
    else:
        # User biasa hanya bisa lihat report miliknya sendiri
        report = get_object_or_404(Report, id=id, reporter=request.user)

    # Kalau admin update status
    if request.method == "POST":
        new_status = request.POST.get("status")
        if request.user.is_staff and new_status in dict(Report.STATUS_CHOICES):
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to {report.get_status_display()}!")

    context = {
        "report": report,
        "last_login": request.COOKIES.get("last_login", "Never"),
    }

    return render(request, "report_detail.html", context)


def is_admin(user):
    return user.is_staff or user.is_superuser

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