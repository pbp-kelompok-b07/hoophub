from django.urls import path
from invoice.views import show_invoices, invoice_detail

app_name = 'invoice'

urlpatterns = [
    path("", show_invoices, name="show_invoices"),
    path("invoice", invoice_detail, name="invoice_detail"),
]