from django.shortcuts import render, redirect, get_object_or_404, reverse
from djaveLogin.login_required import login_required

from invoice.models.invoice import Invoice
from invoice.widgets.edit_invoice import EditInvoice
from invoice.widgets.view_invoice import ViewInvoice
from tracktime.models.project_invoice_rule import ProjectInvoiceRule
from tracktime.views.util import tracktime_context, INVOICES
from tracktime.widgets.project_invoice_rule_table import (
    ProjectInvoiceRuleTable)
from tracktime.widgets.project_invoice_rules_table import (
    ProjectInvoiceRulesTable)
from tracktime.widgets.project_invoices_table import ProjectInvoicesTable


@login_required
def project_invoices(request):
  project_invoice_rules_table = ProjectInvoiceRulesTable(
      request.user, request.POST)
  project_invoices_table = ProjectInvoicesTable(request.user)
  context = tracktime_context(
      INVOICES, request,
      project_invoice_rules_table=project_invoice_rules_table,
      project_invoices_table=project_invoices_table)
  return render(request, 'project_invoices.html', context)


@login_required
def edit_project_invoice(request, pk=None):
  invoice = _get_invoice(request, pk=pk)
  if invoice.paid:
    return redirect(reverse('view_project_invoice', kwargs={'pk': invoice.pk}))

  the_one_thing_on_the_page = None
  the_one_thing_on_the_page = EditInvoice(request, invoice)
  if the_one_thing_on_the_page.deleted():
    return redirect('project_invoices')
  elif the_one_thing_on_the_page.redirect_to():
    return redirect(the_one_thing_on_the_page.redirect_to())

  context = tracktime_context(
      INVOICES, request, the_one_thing_on_the_page=the_one_thing_on_the_page)
  return render(request, 'tracktime_base.html', context)


@login_required
def view_project_invoice(request, pk=None):
  invoice = _get_invoice(request, pk=pk)

  view_invoice = ViewInvoice(invoice, request)

  context = tracktime_context(
      INVOICES, request, the_one_thing_on_the_page=view_invoice)

  return render(request, 'tracktime_base.html', context)


def _get_invoice(request, pk=None):
  return get_object_or_404(Invoice.allowed_by_user_live(request.user), pk=pk)


@login_required
def project_invoice_rule(request, pk=None):
  invoice_rule = None
  if pk:
    invoice_rule = get_object_or_404(
        ProjectInvoiceRule.allowed_by_user_live(request.user), pk=pk)

  table = ProjectInvoiceRuleTable(request.user, request.POST, invoice_rule)
  if table.saved() or table.deleted():
    return redirect('project_invoices')

  context = tracktime_context(INVOICES, request, table=table)
  return render(request, 'project_invoice_rule.html', context)
