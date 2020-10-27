from djaveCRUDTable.columns import LinkColumn

from quickbooks2.models.bill import Bill
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


class Bills(QuickBooksObjects):
  def get_leading_columns(self):
    raise NotImplementedError('get_leading_columns')

  @classmethod
  def get_model(cls):
    return Bill
