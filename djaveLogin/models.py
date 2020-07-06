from secrets import choice

from django.contrib.auth.models import User
from django.shortcuts import reverse
from djaveClassMagic.models.rm_old import RmOldManager, RmOld
from djaveDT import now
from djaveLogin.calc_urls import append_next_url
from django.db import models


def new_token_str():
  """ I guarantee at some point somebody is going to email themselves a login
  link, which they check on their phone, but then they want to log in on a
  desktop computer, but they don't want to log in on their email on the
  computer, so they'll have to copy the token by hand. """
  # Don't include 0, O, o, 1, I, or l.
  non_confusing_characters = (
      'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789')
  return ''.join([choice(non_confusing_characters) for i in range(7)])


# Login URLs
def new_login_token(user):
  return LoginToken.objects.create(user=user, token=new_token_str())


def new_login_url(user, protocol, host, next_url=None):
  return _new_url_helper(protocol, host, new_login_token(user), next_url)


# Sign up URLs
def new_sign_up_token(email):
  token_str = new_token_str()
  token = LoginToken.objects.create(email=email, token=token_str)
  return token


def new_sign_up_url(email, protocol, host):
  return _new_url_helper(protocol, host, new_sign_up_token(email), None)


def _new_url_helper(protocol, host, token, next_url):
  return '{}://{}{}'.format(
      protocol, host, append_next_url(token.next_action_url(), next_url))


def use_token_and_return_user(token_str, nnow=None):
  if not token_str:
    return
  if isinstance(token_str, LoginToken):
    raise Exception(
        'You are supposed to hand the token string to this function, not the '
        'token object')
  nnow = nnow or now()
  existing = LoginToken.objects.filter(
      token=token_str, used__isnull=True).first()
  if existing:
    existing.used = nnow
    existing.save()
    if existing.user:
      return existing.user
    elif existing.email:
      # This just makes sign up links work as log in links, which is especially
      # handy for developing the web demo.
      existing_user = User.objects.filter(email=existing.email).first()
      if existing_user:
        return existing_user
      return User.objects.create(email=existing.email, username=existing.email)
    raise Exception(
        'LoginToken {} has neither user nor email'.format(existing.pk))


class LoginTokenManager(RmOldManager):
  def keep_for_days(self):
    return 7


class LoginToken(RmOld):
  """ A login token represents a single opportunity for a user, or potential
  user, to log in. """
  used = models.DateTimeField(null=True, blank=True, help_text=(
      'Each token is good for one use.'))
  user = models.ForeignKey(
      User, on_delete=models.CASCADE, null=True, blank=True, help_text=(
          'If this user field is populated, this is a login token for that '
          'user.'))
  email = models.CharField(
      max_length=100, null=False, blank=True, default='', help_text=(
          'If this email field is populated, this is a sign up link for '
          'a new user with this email address.'))
  # In practice, len(token_urlsafe()) == 43. Ah but it dawned on me that
  # sometimes people are going to have to manually type in this login link, so
  # I think I should use way fewer characters than that.
  token = models.CharField(max_length=100, null=False, blank=False)

  objects = LoginTokenManager()

  def next_action_url(self):
    """ Either return a URL that will log the user in, or sign up a new user
    with the email address. """
    if self.email:
      return reverse('djave_sign_up', kwargs={'token': self.token})
    elif self.user:
      return reverse('djave_login', kwargs={'token': self.token})
    else:
      raise Exception(self)

  def save(self, *args, **kwargs):
    if int(bool(self.user)) + int(bool(self.email)) != 1:
      raise Exception((
          'Specify precisely one of user and email. You specified {} and {} '
          'respectively').format(self.user, self.email))
    super().save(*args, **kwargs)
