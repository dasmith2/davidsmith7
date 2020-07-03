from djaveAPI.models.publishable import Publishable, LivePublishableManager
from djaveAPI.models.user_api_key import UserAPIKey
from djaveClassMagic.models.base_knows_child import BaseKnowsChild
from djaveClassMagic.signals import destroy_user
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from djmoney.models.fields import MoneyField

from invoice.models.invoice import Invoice


@receiver(destroy_user, sender=Invoice)
def destroy_user_line_items(sender, destroy_object=None, **kwargs):
  for line_item in destroy_object.lineitem_set.all():
    line_item.as_child_class().destroy()


@receiver(post_save)
def save_profile(sender, instance, **kwargs):
  if issubclass(sender, LineItem):
    instance.invoice.calculate_total()


class LiveLineItemManager(LivePublishableManager):
  def get_line_items_from_invoices(self, invoices):
    return self.filter(invoice__in=invoices).select_related(
        'invoice').order_by('invoice')


class LineItem(Publishable, BaseKnowsChild):
  invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, help_text=(
      'What Invoice is this in?'))
  describe_service = models.TextField(help_text=(
      'What did somebody do that was worth charging money for?'))
  amount = MoneyField(max_digits=10, decimal_places=2, help_text=(
      'How much should be charged for this?'))
  amount_calculation = models.TextField(
      null=False, blank=True, default='', help_text=(
          'Describe the exact forumula used to arrive at the amount'))

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(invoice__creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.invoice.creator)

  live = LiveLineItemManager()
