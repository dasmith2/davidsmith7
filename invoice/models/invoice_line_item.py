from djaveAPI.models.publishable import Publishable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveClass.models.base_knows_child import BaseKnowsChild
from django.db import models
from djmoney.models.fields import MoneyField

from invoice.models.invoice import Invoice


class InvoiceLineItem(Publishable, BaseKnowsChild):
  invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT)
  describe_service = models.TextField(help_text=(
      'What did somebody do that was worth charging money for?'))
  amount = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'How much should be charged for this Line Item?'))
  amount_calculation = models.TextField(help_text=(
      'Describe the exact forumula used to arrive at the amount'))

  @classmethod
  def allowed(cls, api_key):
    if isinstance(api_key, UserAPIKey):
      return cls.all.filter(invoice__created_by=api_key.user)
    raise Exception('I dont know which Invoices a {} is allowed to see'.format(
        api_key.__class__))

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.invoice.created_by)
    raise Exception('I dont know how to check which {} can see this Invoice')
