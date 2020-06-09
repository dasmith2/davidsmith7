from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from djaveDT import now
from djmoney.models.fields import MoneyField

from invoice.models.invoice import get_an_invoice_id, Invoice
from tracktime.models.project import Project
from tracktime.models.project_invoice_line_item import ProjectInvoiceLineItem
from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)


class AutoInvoiceConfig(models.Model):
  """ For the time being this is hard coded to automatically create invoices on
  the first of the month. """
  project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text=(
      'What Project should Invoices automatically get created for?'))
  created_by = models.ForeignKey(User, on_delete=models.CASCADE)
  hourly_rate = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'The amount of an invoice will be the hourly_rate * the sum of the '
      'durations of the Work Sessions in that invoice.'))
  first_billable_day = models.DateField(
      default=date(2000, 1, 1), help_text=(
          'These invoices will be automatically created for all un-billed '
          'work sessions on this Project that are on or after this date.'))
  invoice_id_prefix = models.CharField(max_length=10, help_text=(
      'These Invoices gets a unique identifier prefixed with this string'))
  make_payment_to = models.TextField(help_text=(
      'This shows in the upper left hand corner of the invoice. Explain '
      'who you are an how to pay you.'))
  email_to = models.CharField(max_length=200, help_text=(
      'When you click send, where should I email the Invoice?'))
  default_line_item_description = models.TextField(help_text=(
      'When you "Enter time", you create a Work Session. That Work Session '
      'gets turned into an Invoice Line Item whose description is everything '
      'you marked "Done" during that Work Session. If, however, you didn\'t '
      'mark anything done, then the description of that Invoice Line Item '
      'defaults to this field.'))
  net_days = models.PositiveIntegerField(help_text=(
      'How many days after the invoice is sent is it due?'))

  def create_invoice(self, nnow=None):
    nnow = nnow or now()
    descriptions = self._get_descriptions(nnow=nnow)
    if not descriptions.has_work_session_descriptions():
      return
    service_from = (
        descriptions.get_work_session_descriptions()[0].work_session.date)
    invoice = self._create_invoice(
        service_from, self._total(descriptions), nnow=nnow)
    self._create_line_items(invoice, descriptions)
    return invoice

  def _total(self, descriptions):
    total = 0
    for description in descriptions.get_work_session_descriptions():
      total += self._line_item_amount(description)
    return total

  def _create_line_items(self, invoice, descriptions):
    for description in descriptions.get_work_session_descriptions():
      amount = self._line_item_amount(description)
      amount_calculation = '{} hrs * {} / hr'.format(
          description.work_session.hours, self.hourly_rate)
      describe_service = '\n'.join(description.to_do_descriptions)
      if not describe_service:
        describe_service = self.default_line_item_description
      ProjectInvoiceLineItem.live.create(
          invoice=invoice,
          describe_service=describe_service,
          amount=amount,
          amount_calculation=amount_calculation,
          project_work_session=description.work_session)

  def _line_item_amount(self, description):
    return description.work_session.hours * self.hourly_rate

  def _create_invoice(self, service_from, total, nnow=None):
    nnow = nnow or now()
    return Invoice.live.create(
        invoice_id=get_an_invoice_id(self.invoice_id_prefix),
        make_payment_to=self.make_payment_to,
        created_by=self.created_by,
        email_to=self.email_to,
        net_days=self.net_days,
        total=total,
        service_from=service_from,
        service_to=nnow.date())

  def _get_descriptions(self, nnow=None):
    nnow = nnow or now()
    from_date = None
    to_date = nnow.date()
    tz_str = settings.TIME_ZONE
    return ProjectWorkSessionDescriptions(
        self.project, self.created_by, from_date, to_date, tz_str,
        include_invoiced=False)
