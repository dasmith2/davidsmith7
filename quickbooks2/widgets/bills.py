from djaveCRUDTable.columns import LinkColumn
from djaveCRUDTable.filters import hidden_filter

from quickbooks2.models.bill import Bill, Line
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


class Bills(QuickBooksObjects):
  def get_leading_columns(self):
    return [
        LinkColumn('ID', 'url', 'id'),
        LinkColumn('APAccountRef', 'APAccountRef_url', 'APAccountRef_str'),
        'Balance',
        LinkColumn('VendorRef', 'VendorRef_url', 'VendorRef_str')]

  @classmethod
  def get_model(cls):
    return Bill


class Lines(QuickBooksObjects):
  def __init__(self, bill, list_url):
    self.bill = bill
    self.list_url = list_url
    super().__init__()

  def get_leading_columns(self):
    return ['Description', 'Amount']

  def get_list_url(self):
    return self.list_url

  @classmethod
  def get_model(cls):
    return Line

  def get_hidden_filters(self):
    return [hidden_filter('bill', self.bill.pk)]
