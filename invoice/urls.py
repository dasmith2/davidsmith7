from django.urls import path

from invoice.views import mark_invoice_paid, view_invoice


invoice_urls = [
    path('mark_invoice_paid', mark_invoice_paid, name='mark_invoice_paid'),
    path('view_invoice/<pk>', view_invoice, name='view_invoice')]
