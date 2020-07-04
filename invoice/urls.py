from django.urls import path

from invoice.views import view_invoice


invoice_urls = [
    path('view_invoice/<pk>', view_invoice, name='view_invoice')]
