""" QuickBooks has a concept of Bill. This is our local copy. """

from django.db import models
from quickbooks.objects.bill import Bill as QBBill
from quickbooks2.models.account import Account
from quickbooks2.models.quickbooks_object import (
    QuickBooksObject, NestedListQuickBooksObject)
from quickbooks2.models.vendor import Vendor


class Bill(QuickBooksObject):
  APAccountRef = models.ForeignKey(Account, on_delete=models.PROTECT)
  Balance = models.FloatField(default=0.0)
  VendorRef = models.ForeignKey(Vendor, on_delete=models.PROTECT)

  def copy_non_obvious_data(self, qb_bill, nnow=None):
    # self.save() to avoid "ValueError: save() prohibited to prevent data loss
    # due to unsaved related object 'bill'" when you try to save the Lines with
    # a fk to this bill.
    self.save()
    for qb_line in qb_bill.Line:
      Line.merge_obj(self.user, qb_line, nnow=nnow, bill=self)

  @classmethod
  def get_quickbooks_class(cls):
    return QBBill

  def __str__(self):
    return '{} {}'.format(str(self.VendorRef), self.Balance)


class Line(NestedListQuickBooksObject):
  bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
  Description = models.TextField(default='')
  Amount = models.FloatField(default=0.0)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(bill__user=user)

  @classmethod
  def nested_under_model(cls):
    return Bill

  class Meta:
    unique_together = [('bill', 'qb_id')]
