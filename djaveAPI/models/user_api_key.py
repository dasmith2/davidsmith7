from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.api_key import APIKey, APIKeyManager


class UserAPIKeyManager(APIKeyManager):
  def get_user(self, username, plain_password):
    api_key = self.get_api_key(username, plain_password)
    if api_key:
      return api_key.user

  def create_key(self, username, user):
    # I know this function looks redundant, but without it I ran into some
    # confusion about how, exactly, you create a UserAPIKey.
    return super().create_key(username, user=user)


class UserAPIKey(APIKey):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  objects = UserAPIKeyManager()

  def user_can_manage_me(self, user):
    return self.user == user

  def explain_why_can_not_create(self, of_model):
    if isinstance(of_model.new_instance(), User):
      return (
          'User level API keys only have access to a single user. They are '
          'not powerful enough to create new users.')
