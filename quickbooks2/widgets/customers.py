from djaveCRUDTable.columns import LinkColumn

from quickbooks2.models.customer import Customer
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


class Customers(QuickBooksObjects):
  def get_leading_columns(self):
    return [LinkColumn('Name', 'url', 'name')]

  @classmethod
  def get_model(cls):
    return Customer
