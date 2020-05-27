from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.api_key import APIKey, APIKeyManager


class UserAPIKeyManager(APIKeyManager):
  def get_user(self, username, plain_password):
    api_key = self.get_api_key(username, plain_password)
    if api_key:
      return api_key.user


class UserAPIKey(APIKey):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  objects = UserAPIKeyManager()

  def can_delete(self, user):
    return self.user == user
