from datetime import timedelta
import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djaveAPI.models.publishable import Publishable, LivePublishableManager
from djaveAPI.models.user_api_key import UserAPIKey
from djaveClassMagic.models.base_knows_child import BaseKnowsChild
from djaveDT import now, dt_to_d_str, d_to_str, midnight_from_date
from djmoney.models.fields import MoneyField
from djmoney.money import Money


CREATED = 'Created'
DUE = 'Due'
LATE = 'Late'
PAID = 'Paid'

STATUSES = [CREATED, DUE, LATE, PAID]


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
    elif status == DUE:
      qs = qs.filter(paid__isnull=True, due__gte=nnow)
    elif status == LATE:
      qs = qs.filter(paid__isnull=True, due__lte=nnow)
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
      User, related_name='created_invoice', on_delete=models.PROTECT,
      help_text='Who sent this Invoice?')

  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this Invoice created?'))
  sent = models.DateTimeField(null=True, blank=True, help_text=(
      'When was this Invoice sent out?'))
  net_days = models.PositiveIntegerField(help_text=(
      'How many days after the Invoice is sent is it due?'))
  due = models.DateField(null=True, blank=True, help_text=(
      'When is this Invoice due? This field is set automatically on save '
      'according to sent and net_days'))
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
    if self.paid:
      return 'Paid {}'.format(dt_to_d_str(self.paid))
    elif self.sent:
      if self.past_due(nnow=nnow):
        return 'Late. Due {}'.format(d_to_str(self.due))
      return 'Due {}'.format(d_to_str(self.due))
    return 'Created {}'.format(dt_to_d_str(self.created))

  def past_due(self, nnow=None):
    nnow = nnow or now()
    return self.due and self.due < nnow.date()

  def save(self, *args, **kwargs):
    if self.sent and not self.due:
      self.due = (self.sent + timedelta(days=self.net_days)).date()
    super().save(*args, **kwargs)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)
    raise Exception('I dont know how to check which {} can see this Invoice')

  live = LiveInvoiceManager()
