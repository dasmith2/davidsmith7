from datetime import date
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveDT import now
from djmoney.models.fields import MoneyField

from invoice.models.invoice import get_an_invoice_id
from tracktime.models.project import Project
from tracktime.models.project_invoice import ProjectInvoice
from tracktime.models.project_line_item import ProjectLineItem
from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)


class ProjectInvoiceRule(Publishable):
  project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text=(
      'When you run this rule, it will create an Invoice for the work you '
      'did on this Project.'))
  creator = models.ForeignKey(User, on_delete=models.CASCADE, help_text=(
      'Who created this?'))
  hourly_rate = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'How much should I charge per hour for this Project?'))
  first_billable_day = models.DateField(
      default=date(2000, 1, 1), help_text=(
          'When you run this rule, every ProjectWorkSession that hasn\'t '
          'been billed for yet that occurs on or after this date will go in a '
          'new Invoice.'))
  # So, I could make this a SlugField. But I would need to update
  # djaveClassMagic.model_filed.ModelField to include a, like, is_slug
  # attribute, which feels like polluting an abstract idea with details about a
  # particular type or something. Plus, SlugField implies a db index, which I
  # don't want here. So now I think the simplest and easiest thing is to just
  # stick with the rule that explain_why_invalid is for anything more
  # complicated than required fields, basic type checking, and permission.
  invoice_id_prefix = models.CharField(max_length=10, help_text=(
      'Every Invoice created with this rule gets a unique id that starts with '
      'the value of this field.'))
  sent_to = models.TextField(blank=False, null=False, help_text=(
      'This is labeled "Invoice sent to" in the upper left of the Invoice. '
      'Explain who the client is.'))
  make_payment_to = models.TextField(help_text=(
      'This is labeled "Make payment to" in the upper left of the Invoice. '
      'Explain who the service provider is and how to pay them.'))
  default_line_item_description = models.TextField(help_text=(
      'When you "Enter time", you create a ProjectWorkSession. That '
      'gets turned into an InvoiceLineItem whose description '
      'is the descriptions of every ProjectToDo you marked "Done" during that '
      'session. If, however, you didn\'t mark anything done, then the '
      'description of that InvoiceLineItem defaults to the value of this '
      'field.'))
  net_days = models.PositiveIntegerField(help_text=(
      'How many days after the Invoice is sent is it due?'))

  @classmethod
  def model_description(cls):
    return """
        A ProjectInvoiceRule describes how to create a new Invoice for a
        Project."""

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(creator=user).select_related('project')

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)

  def explain_why_invalid(self):
    super_why = super().explain_why_invalid()
    if super_why:
      return super_why
    if re.compile(r'[^\w-]').findall(self.invoice_id_prefix):
      return (
          'The "Invoice id prefix" may contain only '
          'letters, numbers, -, and _')

  def create_invoice(self, nnow=None):
    nnow = nnow or now()
    descriptions = self._get_descriptions(nnow=nnow)
    service_from = nnow.date()
    if descriptions.has_work_session_descriptions():
      service_from = descriptions.earliest_date()
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
      # A ProjectLineItem may exist already. The user could have made an
      # invoice, "deleted" the invoice, then recreated the invoice. Because
      # ProjectInvoice and ProjectLineItems are published on the API,
      # they don't actually get deleted.
      line_item = ProjectLineItem()
      if description.work_session.projectlineitem_or_none:
        line_item = description.work_session.projectlineitem
        line_item.deleted = None
      else:
        line_item.project_work_session = description.work_session
      line_item.invoice = invoice
      line_item.describe_service = describe_service
      line_item.amount = amount
      line_item.amount_calculation = amount_calculation
      line_item.save()

  def _line_item_amount(self, description):
    return description.work_session.hours * self.hourly_rate

  def _create_invoice(self, service_from, total, nnow=None):
    nnow = nnow or now()
    return ProjectInvoice.live.create(
        project=self.project,
        invoice_id=get_an_invoice_id(self.invoice_id_prefix),
        sent_to=self.sent_to,
        make_payment_to=self.make_payment_to,
        creator=self.creator,
        net_days=self.net_days,
        total=total,
        service_from=service_from,
        service_to=nnow.date())

  def _get_descriptions(self, nnow=None):
    nnow = nnow or now()
    from_date = self.first_billable_day
    to_date = nnow.date()
    tz_str = settings.TIME_ZONE
    return ProjectWorkSessionDescriptions(
        self.project, self.creator, from_date, to_date, tz_str,
        include_invoiced=False)
