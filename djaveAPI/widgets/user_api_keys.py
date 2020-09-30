from djaveCRUDTable.columns import (
    DisplayFieldColumn, DeleteColumn, ReadonlyFieldColumn, EditFieldColumn)
from djaveCRUDTable.crud_table import CRUDTable
from djaveHTML.h import H2
from djaveHTML.paragraph import Paragraph
from djaveHTML.wrapper import Wrapper

from djaveAPI.models.user_api_key import UserAPIKey


class UserAPIKeys(CRUDTable):
  def __init__(self, list_url):
    username_column = DisplayFieldColumn(
        'API Key username', 'username', model=UserAPIKey)
    password_column = ReadonlyFieldColumn(
        'API Key password', 'plain_password', model=UserAPIKey)
    webhook_url_column = EditFieldColumn(UserAPIKey, 'webhook_url')
    display_columns = [
        username_column, password_column, webhook_url_column, DeleteColumn()]
    description = (
        'User API Keys will retrieve data based on what you, the user, can '
        'see on the website.')
    list_header = Wrapper(H2('User API Keys'), Paragraph(description))
    super().__init__(
        UserAPIKey, display_columns, list_url=list_url,
        list_header=list_header, margin_top_css='margin-top-half',
        inline_create=True)
