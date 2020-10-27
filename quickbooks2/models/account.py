""" QuickBooks has a concept of Account. This is our local copy. """

from django.db import models
from quickbooks.objects.account import Account as QBAccount
from quickbooks2.models.quickbooks_object import QuickBooksObject


class Account(QuickBooksObject):
  Name = models.CharField(max_length=200, default='')
  Classification = models.CharField(max_length=200, default='')
  AccountType = models.CharField(max_length=200, default='')

  @classmethod
  def get_quickbooks_class(cls):
    return QBAccount

  def __str__(self):
    return self.Name
