from django.shortcuts import render, get_object_or_404
from djaveLogin.login_required import login_required

from invoice.models import Invoice
from invoice.widgets.view_invoice import ViewInvoice


@login_required
def view_invoice(request, pk):
  invoice = get_object_or_404(
      Invoice.allowed_by_user_live(request.user), pk=pk)
  context = {'invoice': ViewInvoice(invoice, request)}
  return render(request, 'view_invoice_page.html', context)
