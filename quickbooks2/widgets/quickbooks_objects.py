from djaveCRUDTable.columns import DisplayFieldColumn
from djaveCRUDTable.crud_table import CRUDTable

from quickbooks2.list_url import list_url


class QuickBooksObjects(CRUDTable):
  def __init__(self):
    super().__init__(
        self.get_model(), self.get_display_columns(),
        list_url=list_url(self.get_model()),
        can_create_new=False, list_header=None)

  def get_display_columns(self):
    return self.get_leading_columns() + [
        DisplayFieldColumn('Quickbooks ID', 'qb_id'),
        DisplayFieldColumn('Last synced', 'last_synced_str')]

  def get_leading_columns(self):
    return []

  @classmethod
  def get_model(cls):
    raise NotImplementedError('get_model')
