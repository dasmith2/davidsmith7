from datetime import timedelta
import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from djaveAPI.models.publishable import Publishable, LivePublishableManager
from djaveAPI.models.user_api_key import UserAPIKey
from djaveClassMagic.models.base_knows_child import BaseKnowsChild
from djaveClassMagic.signals import destroy_user
from djaveDT import now, dt_to_d_str, d_to_str, midnight_from_date
from djaveTable.cell_content import Tooltip
from djmoney.models.fields import MoneyField
from djmoney.money import Money


@receiver(destroy_user, sender=User)
def destroy_user_invoices(sender, destroy_object=None, **kwargs):
  for invoice in destroy_object.createdinvoice_set.all():
    destroy_user.send(sender=Invoice, destroy_object=invoice)
    invoice.as_child_class().destroy()


CREATED = 'Created'
SENDING = 'Sending'
DUE = 'Due'
LATE = 'Late'
PAID = 'Paid'

STATUSES = [CREATED, SENDING, DUE, LATE, PAID]


STATUS_HELP_TEXT = """
    Created invoices don't have a sent date yet. Sending invoices have a sent
    date in the future. Due invoices were sent already, but aren't due yet.
    Late invoices have a due date in the past. Paid invoices have a paid
    date."""
STATUS_TOOLTIP = Tooltip('Status', STATUS_HELP_TEXT, width=400)


def get_an_invoice_id(invoice_id_prefix, nnow=None):
  nnow = nnow or now()
  date_part = nnow.date().strftime('%Y%m%d')
  next_attempt = '{}{}'.format(invoice_id_prefix, date_part)
  attempt = 1
  while Invoice.objects.filter(invoice_id=next_attempt).exists():
    attempt += 1
    next_attempt = '{}{}_{}'.format(invoice_id_prefix, date_part, attempt)
  return next_attempt


class LiveInvoiceManager(LivePublishableManager):
  def get_important_invoices(self, user, nnow=None):
    """ This goes in a table titled "Unpaid invoices" but it's really, like,
    unpaid or recently paid invoices, but it's really, like, important
    invoices. """
    nnow = nnow or now()
    paid_cutoff = nnow - timedelta(days=2)
    return self.allowed_by_user(user).filter(
        Q(paid__isnull=True) | Q(paid__gte=paid_cutoff)).order_by('-pk')

  def get_invoices(
      self, user, created_from=None, created_to=None, status=None, nnow=None):
    nnow = nnow or now()
    qs = self.allowed_by_user(user)
    if created_from:
      qs = qs.filter(created__gte=midnight_from_date(created_from))
    if created_to:
      cutoff = midnight_from_date(created_to) + timedelta(days=1)
      qs = qs.filter(created__lte=cutoff)
    if status == CREATED:
      qs = qs.filter(sent__isnull=True)
    elif status == SENDING:
      qs = qs.filter(sent__gt=nnow.date())
    elif status == DUE:
      qs = qs.filter(
          paid__isnull=True, sent__lte=nnow.date(), due__gte=nnow.date())
    elif status == LATE:
      qs = qs.filter(paid__isnull=True, due__lt=nnow.date())
    elif status == PAID:
      qs = qs.filter(paid__isnull=False)
    return qs.order_by('pk')


class Invoice(Publishable, BaseKnowsChild):
  invoice_id = models.CharField(max_length=100, unique=True, help_text=(
      'A unique string that identifies an Invoice. I know that Invoices '
      'already have an id, but that id doesn\'t include a prefix string '
      'and accountants seem to like that.'))

  sent_to = models.TextField(blank=False, null=False, help_text=(
      'This is labeled "Sent to" in the upper left of the Invoice. Explain '
      'who the client is.'))
  make_payment_to = models.TextField(help_text=(
      'This is labeled "Make payment to" in the upper left of the Invoice. '
      'Explain who the service provider is, and how to pay them.'))

  creator = models.ForeignKey(
      User, related_name='createdinvoice_set', on_delete=models.PROTECT,
      help_text='Who sent this Invoice?')

  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this Invoice created?'))
  sent = models.DateField(null=True, blank=True, help_text=(
      'When was this Invoice sent out, or when will it be sent out?'))
  net_days = models.PositiveIntegerField(help_text=(
      'How many days after the Invoice is sent is it due?'))
  due = models.DateField(null=True, blank=True, help_text=(
      'The due date is set automatically based on the Sent date and Net Days'))
  paid = models.DateTimeField(null=True, blank=True, help_text=(
      'When was this Invoice marked paid?'))

  total = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'What is the total amount due for this Invoice?'))
  service_from = models.DateField(help_text=(
      'An Invoice is for service that happened between a from date and a to '
      'date'))
  service_to = models.DateField(help_text=(
      'An Invoice is for service that happened between a from date and a to '
      'date'))

  def mark_deleted(self, nnow=None):
    for line_item in self.lineitem_set.all():
      line_item.as_child_class().mark_deleted(nnow=nnow)
    super().mark_deleted(nnow=nnow)

  def calculate_total(self):
    self.total = Money(0, 'USD')
    for line_item in self.lineitem_set.all():
      if not line_item.deleted:
        self.total += line_item.amount
    self.save()

  def status(self, nnow=None):
    return re.compile(r'^\w+').findall(self.status_with_date(nnow=nnow))[0]

  def status_with_date(self, nnow=None):
    nnow = nnow or now()
    if self.paid:
      return 'Paid {}'.format(dt_to_d_str(self.paid))
    elif self.sent:
      if self.past_due(nnow=nnow):
        return 'Late. Due {}'.format(d_to_str(self.due))
      if self.sent <= nnow.date():
        return 'Due {}'.format(d_to_str(self.due))
      return 'Sending {}'.format(d_to_str(self.sent))
    return 'Created {}'.format(dt_to_d_str(self.created))

  def add_to_json(self, existing_json):
    existing_json['status'] = self.status()
    existing_json['status_with_date'] = self.status_with_date()

  def past_due(self, nnow=None):
    nnow = nnow or now()
    return self.due and self.due < nnow.date()

  def save(self, *args, **kwargs):
    if self.sent:
      self.due = (self.sent + timedelta(days=self.net_days))
    else:
      self.due = None
    super().save(*args, **kwargs)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)
    raise Exception('I dont know how to check which {} can see this Invoice')

  live = LiveInvoiceManager()
