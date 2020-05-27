from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.widgets.new_api_key_widget import NewAPIKeyTable


class NewUserAPIKeyTable(NewAPIKeyTable):
  def __init__(self, user, request_POST):
    self.user = user
    super().__init__(request_POST)

  def existing_keys(self):
    return UserAPIKey.objects.filter(user=self.user).order_by('-pk')

  def create_key(self, username):
    return UserAPIKey.objects.create_key(username, user=self.user)
