from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from djaveLogin.models import use_token_and_return_user


class AuthenticationBackend(BaseBackend):
  def authenticate(self, request, token=None):
    return use_token_and_return_user(token)

  def get_user(self, user_id):
    return User.objects.filter(pk=user_id).first()
