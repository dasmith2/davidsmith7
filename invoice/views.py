from django.shortcuts import render
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_request_ajax_obj
from djaveDT import now
from djaveLogin.login_required import login_required

from invoice.models import Invoice
from invoice.widgets.view_invoice import ViewInvoice


@ajax_endpoint_login_required
def mark_invoice_paid(request):
  invoice = get_request_ajax_obj(request, model=Invoice)
  invoice.paid = now()
  invoice.save()


@login_required
def view_invoice(request, pk):
  invoice = get_request_ajax_obj(request, model=Invoice, pk=pk)
  context = {'invoice': ViewInvoice(invoice, request)}
  return render(request, 'view_invoice_page.html', context)
