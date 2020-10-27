""" QuickBooks has a concept of Customer. This is our local copy. """

from django.db import models
from quickbooks.objects.customer import Customer as QBCustomer
from quickbooks2.models.quickbooks_object import QuickBooksObject


def qb_customer_name(qb_customer):
  """ Sometimes they don't have a DisplayName, so, I guess try a bunch
  of other attributes as well. """
  return qb_customer.DisplayName or qb_customer.FullyQualifiedName or (
      qb_customer.PrintOnCheckName or qb_customer.Title or (
          qb_customer.CompanyName or qb_customer.FamilyName))


class Customer(QuickBooksObject):
  name = models.CharField(max_length=200)

  def populate_extra_fields(self, obj_from_quickbooks):
    self.name = qb_customer_name(obj_from_quickbooks)

  @classmethod
  def get_quickbooks_class(cls):
    return QBCustomer

  def __str__(self):
    return self.name
