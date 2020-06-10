from datetime import timedelta
from random import randint

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveClass.models.base_knows_child import BaseKnowsChildTransition
from djaveDT import now
from djmoney.models.fields import MoneyField


def get_an_invoice_id(invoice_id_prefix):
  return '{}{}'.format(invoice_id_prefix, randint(1000000, 2000000))


class Invoice(Publishable, BaseKnowsChildTransition):
  invoice_id = models.CharField(max_length=100, unique=True, help_text=(
      'A unique string that identifies an Invoice. I know that Invoices '
      'already have an id, but that id doesn\'t include a prefix string '
      'and accountants seem to like that.'))

  make_payment_to = models.TextField(help_text=(
      'This shows in the upper left hand corner of the Invoice. Explain '
      'who you are an how to pay you.'))

  created_by = models.ForeignKey(
      User, related_name='created_invoice', on_delete=models.PROTECT,
      help_text='Who sent this Invoice?')

  created = models.DateTimeField(auto_now_add=True, help_text=(
      'When was this Invoice created?'))
  sent = models.DateTimeField(null=True, blank=True, help_text=(
      'When was this Invoice sent out?'))
  email_to = models.CharField(max_length=200, help_text=(
      'Who should this Invoice be emailed to?'))
  net_days = models.PositiveIntegerField(help_text=(
      'How many days after the Invoice is sent is it due?'))
  due = models.DateTimeField(null=True, blank=True, help_text=(
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
    for line_item in self.invoicelineitem_set.all():
      line_item.as_child_class().mark_deleted(nnow=nnow)
    super().mark_deleted(nnow=nnow)

  def status(self, nnow=None):
    if self.paid:
      return 'Paid'
    elif self.sent:
      if self.past_due(nnow=nnow):
        return 'Past due'
      return 'Sent'
    return 'New'

  def past_due(self, nnow=None):
    nnow = nnow or now()
    return self.due and self.due < nnow

  def save(self, *args, **kwargs):
    if self.sent:
      self.due = self.sent + timedelta(days=self.net_days)
    super().save(*args, **kwargs)

  @classmethod
  def allowed(cls, api_key):
    if isinstance(api_key, UserAPIKey):
      return cls.all.filter(created_by=api_key.user)
    raise Exception('I dont know which Invoices a {} is allowed to see'.format(
        api_key.__class__))

  @classmethod
  def allowed_for_user_live(cls, user):
    return cls.live.filter(created_by=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.created_by)
    raise Exception('I dont know how to check which {} can see this Invoice')
