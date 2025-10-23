from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from report.forms import ReportForm
from report.models import Report
from review.models import Review
from catalog.models import Product

# Create your views here.
LOGIN_URL = '/authentication/login/'

@login_required(login_url=LOGIN_URL)
def show_report(request):

    report_list = Report.objects.filter(reporter=request.user)

    context = {
        'report_list': report_list,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }
    return render(request, 'report.html', context)

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
def delete_report(request, id):
    report = get_object_or_404(Report, pk=id)
    report.delete()
    messages.success(request, "Report deleted successfully!")
    return HttpResponseRedirect(reverse('report:show_report'))

@login_required(login_url=LOGIN_URL)
def report_detail(request, id):
    report = get_object_or_404(Report, id=id, reporter=request.user)

    context = {
        'report': report,
        'last_login': request.COOKIES.get('last_login', 'Never')
    }

    return render(request, 'report_detail.html', context)