from django.shortcuts import render
from djaveAPI.get_request_variable import get_request_ajax_obj
from djaveLogin.login_required import login_required

from invoice.models import Invoice
from invoice.widgets.view_invoice import ViewInvoice


@login_required
def view_invoice(request, pk):
  invoice = get_request_ajax_obj(request, model=Invoice, pk=pk)
  context = {'invoice': ViewInvoice(invoice, request)}
  return render(request, 'view_invoice_page.html', context)
