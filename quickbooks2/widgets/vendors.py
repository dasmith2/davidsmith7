from djaveCRUDTable.columns import LinkColumn

from quickbooks2.models.vendor import Vendor
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


class Vendors(QuickBooksObjects):
  def get_leading_columns(self):
    return [LinkColumn('Name', 'url', 'name')]

  @classmethod
  def get_model(cls):
    return Vendor
