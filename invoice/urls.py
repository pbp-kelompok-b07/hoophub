from django.urls import path
from invoice.views import show_invoices, invoice_detail, create_invoice, invoice_detail_json, reorder_invoice, delete_invoice, update_status, show_invoice_json_flutter, create_invoice_flutter, delete_invoice_flutter, reorder_flutter, edit_status_flutter

app_name = 'invoice'

urlpatterns = [
    path("", show_invoices, name="show_invoices"),
    path("<uuid:id>/", invoice_detail, name="invoice_detail"),
    path("create/", create_invoice, name="create_invoice"),
    path("<uuid:id>/json/", invoice_detail_json, name="invoice_detail_json"),
    path("<uuid:id>/reorder/", reorder_invoice, name="reorder"),
    path("<uuid:id>/delete/", delete_invoice, name="delete"),
    path('<uuid:id>/update-status/', update_status, name='update_status'),
    path('json/', show_invoice_json_flutter, name='show_invoice_json_flutter'),
    path('create-flutter/', create_invoice_flutter, name='create_invoice_flutter'),
    path('delete-invoice-flutter/', delete_invoice_flutter, name='delete_invoice_flutter'),
    path('reorder-flutter/', reorder_flutter, name='reorder_flutter'),
    path('edit-status-flutter/', edit_status_flutter, name='edit_status_flutter'),
]
