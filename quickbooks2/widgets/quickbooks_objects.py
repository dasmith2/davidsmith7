from djaveCRUDTable.columns import DisplayFieldColumn
from djaveCRUDTable.crud_table import CRUDTable, USE_DEFAULT

from quickbooks2.list_url import list_url


class QuickBooksObjects(CRUDTable):
  def __init__(self):
    super().__init__(
        self.get_model(), self.get_display_columns(),
        list_url=self.get_list_url(),
        can_create_new=False, list_header=None,
        hidden_filters=self.get_hidden_filters())

  def get_list_url(self):
    return list_url(self.get_model())

  def get_hidden_filters(self):
    return USE_DEFAULT

  def get_display_columns(self):
    return self.get_leading_columns() + [
        DisplayFieldColumn('Quickbooks ID', 'qb_id'),
        DisplayFieldColumn('Last synced', 'last_synced_str')]

  def get_leading_columns(self):
    return []

  @classmethod
  def get_model(cls):
    raise NotImplementedError('get_model')
