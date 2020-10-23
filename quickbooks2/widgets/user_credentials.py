from django.shortcuts import reverse
from djaveCRUDTable.crud_table import CRUDTable

from quickbooks2.models.user_credentials import (
    UserCredentials as UserCredentialsModel)


class UserCredentials(CRUDTable):
  def __init__(self):
    super().__init__(
        UserCredentialsModel, ['refresh_token_updated_at'],
        list_url=reverse('auth_stuff'), can_create_new=False, list_header=None)
