from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from djaveDT import now
from djmoney.models.fields import MoneyField

from invoice.models.invoice import get_an_invoice_id
from tracktime.models.project import Project
from tracktime.models.project_invoice import ProjectInvoice
from tracktime.models.project_line_item import ProjectLineItem
from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)


class ProjectInvoiceRule(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE, help_text=(
      'When you run this rule, it will create an Invoice for the work you '
      'did on this project.'))
  creator = models.ForeignKey(User, on_delete=models.CASCADE)
  hourly_rate = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'How much should I charge per hour you spent on this project?'))
  first_billable_day = models.DateField(
      default=date(2000, 1, 1), help_text=(
          'Every work session that hasn\'t been billed for yet that occurs '
          'after this cutoff date will go in an Invoice when you run this '
          'rule.'))
  invoice_id_prefix = models.CharField(max_length=10, help_text=(
      'Every Invoice you make with this rule will get a unique id. That '
      'unique id will start with what you put here.'))
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
      'How many days after the Invoice is sent is it due?'))

  @classmethod
  def allowed_by_user(cls, user):
    return cls.objects.filter(creator=user).select_related('project')

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
        make_payment_to=self.make_payment_to,
        creator=self.creator,
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
        self.project, self.creator, from_date, to_date, tz_str,
        include_invoiced=False)
