""" QuickBooks has a concept of Bill. This is our local copy. """

from django.contrib.auth.models import User
from django.db import models
from quickbooks.objects.base import Ref
from quickbooks.objects.bill import Bill as QBBill
from quickbooks.objects.detailline import (
    AccountBasedExpenseLine, AccountBasedExpenseLineDetail)

from quickbooks2.models.account import Account
from quickbooks2.models.quickbooks_object import (
    QuickBooksObject, NestedListQuickBooksObject)
from quickbooks2.models.vendor import Vendor


def get_bill_to_create(amount, description):
  bill = Line.objects.first().bill

  vendor = bill.VendorRef
  qb_vendor = Ref()
  qb_vendor.value = vendor.qb_id

  ap_account = bill.APAccountRef
  qb_ap_account = Ref()
  qb_ap_account.value = ap_account.qb_id

  expense_account = Account.objects.get(qb_id=20, Name='Supplies')
  qb_ex_account = Ref()
  qb_ex_account.value = expense_account.qb_id

  qb_line_detail = AccountBasedExpenseLineDetail()
  qb_line_detail.AccountRef = qb_ex_account

  qb_line = AccountBasedExpenseLine()
  qb_line.Description = description
  qb_line.Amount = amount
  qb_line.AccountBasedExpenseLineDetail = qb_line_detail

  qb_bill = QBBill()
  qb_bill.VendorRef = qb_vendor
  qb_bill.APAccountRef = qb_ap_account
  qb_bill.Line = [qb_line]

  return qb_bill


def create_bill(qb_bill):
  def do_create(qb):
    qb_bill.save(qb=qb)
    return qb_bill

  try:
    return User.objects.first().usercredentials.do_query(
        'https://davidsmith7-stage.herokuapp.com', do_create)
  except Exception as ex:
    return ex


def get_bill(qb_id):
  def do_get(qb):
    return QBBill.get(qb_id, qb)

  try:
    return User.objects.first().usercredentials.do_query(
        'https://davidsmith7-stage.herokuapp.com', do_get)
  except Exception as ex:
    return ex


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
  Description = models.TextField(default='', null=True, blank=True)
  Amount = models.FloatField(default=0.0)
  AccountRef = models.ForeignKey(
      Account, on_delete=models.PROTECT, blank=True, null=True, help_text=(
          'A Line could, I believe, have an ItemBasedExpenseLineDetail in '
          'which case there wont be an Account.'))

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(bill__user=user)

  @classmethod
  def nested_under_model(cls):
    return Bill

  def copy_non_obvious_data(self, qb_line, nnow=None):
    if hasattr(qb_line, 'AccountBasedExpenseLineDetail'):
      # I thiiiiink it's possible for a Line to have an
      # ItemBasedExpenseLineDetail instead.
      self.AccountRef = Account.objects.get(
          qb_id=qb_line.AccountBasedExpenseLineDetail.AccountRef.value)

  class Meta:
    unique_together = [('bill', 'qb_id')]

  def __repr__(self):
    return f"{self.Description} {self.Amount}"
