from secrets import token_urlsafe

from django.contrib.auth.models import User
from django.shortcuts import reverse
from djaveClass.rm_old_manager import RmOldManager
from djaveDT import now
from djaveURL import is_valid_url, protocol_and_host
from django.db import models


NEXT_URL = 'next_url'


def new_token(user):
  token = token_urlsafe()
  LoginToken.objects.create(user=user, token=token)
  return token


def new_login_url(user, request, next_url=None):
  """ If the given user goes to this url, they'll get logged in. """
  return '{}{}'.format(
      protocol_and_host(request),
      new_relative_login_url(user, next_url=next_url))


def new_relative_login_url(user, next_url=None):
  """ If the given user goes to this url, they'll get logged in. """
  url = reverse('djave_login', kwargs={'token': new_token(user)})
  return append_next_url(url, next_url)


def append_next_url(url, next_url):
  if not next_url:
    return url
  if not is_valid_url(next_url):
    raise Exception(
        'I double checked, and {} is not a valid next_url'.format(next_url))
  return '{}?{}={}'.format(url, NEXT_URL, next_url)


def use_token_and_return_user(token, nnow=None):
  if not token:
    return
  nnow = nnow or now()
  existing = LoginToken.objects.filter(token=token, used__isnull=True).first()
  if existing:
    existing.used = nnow
    existing.save()
    return existing.user


class LoginTokenManager(RmOldManager):
  def keep_for_days(self):
    return 7


class LoginToken(models.Model):
  """ A login token represents a single opportunity for a particular user to
  log in. """
  created = models.DateTimeField(auto_now_add=True)
  used = models.DateTimeField(null=True, blank=True, help_text=(
      'Each token is good for one use.'))
  user = models.ForeignKey(
      User, on_delete=models.CASCADE, null=False, blank=False)
  # In practice, len(token_urlsafe()) == 43
  token = models.CharField(max_length=100, null=False, blank=False)

  objects = LoginTokenManager()
