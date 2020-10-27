from djaveCRUDTable.columns import LinkColumn

from quickbooks2.models.account import Account
from quickbooks2.widgets.quickbooks_objects import QuickBooksObjects


class Accounts(QuickBooksObjects):
  def get_leading_columns(self):
    return [
        LinkColumn('Name', 'url', 'name'), 'Classification', 'AccountType']

  @classmethod
  def get_model(cls):
    return Account
