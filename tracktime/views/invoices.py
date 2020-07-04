
from django.shortcuts import render, redirect, get_object_or_404, reverse
from djaveLogin.login_required import login_required
from djaveTable.cell_content import Tooltip
from djaveCSV import CanCSVResponse, CanCSV

from invoice.models.invoice import Invoice
from invoice.widgets.edit_invoice import EditInvoice
from invoice.widgets.view_invoice import ViewInvoice
from tracktime.models.project_invoice import ProjectInvoice
from tracktime.models.project_invoice_rule import ProjectInvoiceRule
from tracktime.views.util import tracktime_context, INVOICES
from tracktime.widgets.all_project_invoices import AllProjectInvoices
from tracktime.widgets.all_project_line_items import AllProjectLineItems
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

  unpaid_help_text = 'Well, technically, unpaid and recently paid.'
  invoice_rule_help_text = (
      'An Invoice Rule has a "Create new invoice" button. When you click '
      'that button,')
  if project_invoice_rules_table.has_rules():
    invoice_rule_help_text = (
        'When you click the "Create new invoice" button,')
  invoice_rule_help_text += (
      ' it will find all un-invoiced work for that '
      'project and put it in an Invoice.')
  invoice_rules_header = Tooltip(
      'Invoice rules', invoice_rule_help_text, width=300)

  invoices_exist = ProjectInvoice.live.allowed_by_user(request.user).exists()

  context = tracktime_context(
      INVOICES,
      project_invoice_rules_table=project_invoice_rules_table,
      project_invoices_table=project_invoices_table,
      invoice_rules_header=invoice_rules_header,
      the_word_unpaid=Tooltip('Unpaid', unpaid_help_text),
      invoices_exist=invoices_exist,
      all_invoices_url=reverse('all_project_invoices'))
  return render(request, 'project_invoices.html', context)


@login_required
@CanCSV
def all_project_invoices(request):
  report = AllProjectInvoices(request.user, request.GET)
  context = tracktime_context(
      INVOICES, request, the_one_thing_on_the_page=report)
  return CanCSVResponse(
      'tracktime_base.html', context, report.table, 'invoices.csv')


@login_required
@CanCSV
def project_line_items(request):
  report = AllProjectLineItems(request.user, request.GET)
  context = tracktime_context(
      INVOICES, request, the_one_thing_on_the_page=report, title='Line items')
  return CanCSVResponse(
      'tracktime_base.html', context, report.table, 'line_items.csv')


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

  return render(request, 'blank.html', context)


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
