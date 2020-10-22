from django.shortcuts import reverse
from djaveCRUDTable.columns import DisplayFieldColumn, LinkColumn
from djaveCRUDTable.crud_table import CRUDTable

from quickbooks2.models.customer import Customer


class Customers(CRUDTable):
  def __init__(self):
    display_columns = [
        LinkColumn('Name', 'url', 'name'),
        DisplayFieldColumn('Quickbooks ID', 'qb_id'),
        DisplayFieldColumn('Last synced', 'last_synced_str')]
    super().__init__(
        Customer, display_columns, list_url=reverse('qb2_customers'),
        can_create_new=False, list_header=None)

  def __str__(self):
    return self.name
