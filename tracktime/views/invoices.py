from django.shortcuts import render, redirect, get_object_or_404
from djaveLogin.login_required import login_required

from invoice.models.invoice import Invoice
from invoice.widgets.edit_invoice import EditInvoice
from invoice.widgets.display_invoice import DisplayInvoice
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
def project_invoice(request, pk=None):
  invoice = None
  if pk:
    invoice = get_object_or_404(
        Invoice.allowed_for_user_live(request.user), pk=pk)

  the_one_thing_on_the_page = None
  if not invoice.paid:
    the_one_thing_on_the_page = EditInvoice(request, invoice)
    if the_one_thing_on_the_page.deleted():
      return redirect('project_invoices')
  else:
    the_one_thing_on_the_page = DisplayInvoice(invoice)

  context = tracktime_context(
      INVOICES, request, the_one_thing_on_the_page=the_one_thing_on_the_page)
  return render(request, 'tracktime_base.html', context)


@login_required
def project_invoice_rule(request, pk=None):
  invoice_rule = None
  if pk:
    invoice_rule = get_object_or_404(
        ProjectInvoiceRule.allowed_for_user_live(request.user), pk=pk)

  table = ProjectInvoiceRuleTable(request.user, request.POST, invoice_rule)
  if table.saved() or table.deleted():
    return redirect('project_invoices')

  context = tracktime_context(INVOICES, request, table=table)
  return render(request, 'project_invoice_rule.html', context)
