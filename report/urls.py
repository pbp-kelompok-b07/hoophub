from django.urls import path
from report.views import create_report_ajax, edit_report, show_report, delete_report

app_name = 'report'

urlpatterns = [
    path('', show_report, name='show_report'),
    path('create/', create_report_ajax, name='create_report'),
    path('edit/<uuid:id>/', edit_report, name='edit_report'),
    path('delete/<uuid:id>', delete_report, name="delete_report")
]