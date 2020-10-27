""" QuickBooks has a concept of Vendor. This is our local copy. """

from django.db import models
from quickbooks.objects.vendor import Vendor as QBVendor
from quickbooks2.models.quickbooks_object import QuickBooksObject


def qb_vendor_name(qb_vendor):
  """ Vendors seem to always have a DisplayName. """
  return qb_vendor.DisplayName or qb_vendor.Title or (
      qb_vendor.GivenName or qb_vendor.FamilyName)


class Vendor(QuickBooksObject):
  name = models.CharField(max_length=200)

  def populate_extra_fields(self, obj_from_quickbooks):
    self.name = qb_vendor_name(obj_from_quickbooks)

  @classmethod
  def get_quickbooks_class(cls):
    return QBVendor

  def __str__(self):
    return self.name
