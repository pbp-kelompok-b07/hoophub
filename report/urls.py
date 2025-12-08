from django.urls import path
from report.views import create_report_ajax, edit_report, show_report, delete_report, report_detail, admin_report_detail, admin_report_list, show_json_flutter, proxy_image, create_report_flutter

app_name = 'report'

urlpatterns = [
    path('', show_report, name='show_report'),
    path('create/', create_report_ajax, name='create_report'),
    path('edit/<uuid:id>/', edit_report, name='edit_report'),
    path('delete/<uuid:id>/', delete_report, name="delete_report"),
    path('detail/<uuid:id>/', report_detail, name='report_detail'),
    path('admin/reports/', admin_report_list, name='admin_report_list'),
    path('admin/reports/<uuid:report_id>/', admin_report_detail, name='admin_report_detail'),
    path('json-flutter/', show_json_flutter, name='show_json_flutter'),
    path('create-flutter/', create_report_flutter, name='create_report_flutter'),
    path('proxy-image/', proxy_image, name='proxy_image'),
]