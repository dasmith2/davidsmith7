from django.shortcuts import render, redirect, get_object_or_404, reverse
from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.get_instance import get_instance
from djaveAPI.views.api import (
    do_list_or_save_new, do_get_save_or_delete_existing)
from djaveLogin.login_required import login_required
from djaveCSV import CanCSVResponse, CanCSV

from invoice.models.invoice import Invoice
from invoice.widgets.edit_invoice import EditInvoice
from invoice.widgets.line_items import LineItems
from invoice.widgets.view_invoice import ViewInvoice
from tracktime.models.project_invoice import ProjectInvoice
from tracktime.models.project_invoice_rule import ProjectInvoiceRule
from tracktime.views.nav_context import tracktime_context, INVOICES
from tracktime.widgets.all_project_line_items import AllProjectLineItems
from tracktime.widgets.project_invoice_rules import ProjectInvoiceRules
from tracktime.widgets.project_invoices import (
    ProjectInvoices, AllProjectInvoices)


@login_required
def project_invoices(request):
  project_invoice_rules = ProjectInvoiceRules(request.user)
  project_invoices = ProjectInvoices(request.user)

  line_items = LineItems()

  invoices_exist = ProjectInvoice.live.allowed_by_user(request.user).exists()

  context = tracktime_context(
      request.user, INVOICES,
      project_invoice_rules_table=project_invoice_rules,
      project_invoices=project_invoices,
      line_items=line_items,
      invoices_exist=invoices_exist,
      all_invoices_url=reverse('all_project_invoices'))
  return render(request, 'project_invoices.html', context)


@ajax_or_api_endpoint_authenticated
def create_invoice(request_method, request_dict, credentials):
  project_invoice_rule_id = get_request_variable(
      request_dict, 'project_invoice_rule_id')
  project_invoice_rule = get_instance(
      ProjectInvoiceRule.live, project_invoice_rule_id, credentials)
  project_invoice_rule.create_invoice()


@login_required
@CanCSV
def all_project_invoices(request):
  all_invoices = AllProjectInvoices(request.user)
  context = tracktime_context(
      request.user, INVOICES, all_invoices=all_invoices,
      all_line_items_url=reverse('project_line_items'))
  return CanCSVResponse(
      'all_project_invoices.html', context, all_invoices, 'invoices.csv')


@login_required
@CanCSV
def project_line_items(request):
  all_line_items = AllProjectLineItems(request.user)
  context = tracktime_context(
      request.user, INVOICES, the_one_thing_on_the_page=all_line_items)
  return CanCSVResponse(
      'tracktime_base.html', context, all_line_items, 'line_items.csv')


@login_required
def view_project_invoice(request, pk=None):
  invoice = _get_invoice(request, pk=pk)

  view_invoice = ViewInvoice(invoice, request)

  context = tracktime_context(
      request.user, INVOICES, the_one_thing_on_the_page=view_invoice)

  return render(request, 'blank.html', context)


def _get_invoice(request, pk=None):
  return get_object_or_404(Invoice.allowed_by_user_live(request.user), pk=pk)


@ajax_or_api_endpoint_authenticated
def list_or_save_new_line_item(request_method, request_dict, credentials):
  """ These views exist so that the UI can have an API endpoint that will list
  all LineItems regarldess of subclass, will update just the LineItem fields,
  when you save a new line item it will create a ManualLineItem. """
  if request_method == 'GET':
    return do_list_or_save_new(  # Well, do_list basically.
        request_method, request_dict, credentials, 'LineItem')
  return do_list_or_save_new(  # Well, do_save_new basically.
      request_method, request_dict, credentials, 'ManualLineItem')


@ajax_or_api_endpoint_authenticated
def get_save_or_delete_existing_line_item(
    request_method, request_dict, credentials, pk):
  return do_get_save_or_delete_existing(
      request_method, request_dict, credentials, 'LineItem', pk)
