"""
This class is for any state you might want to hold on to as part of doing an
OAuth2.0 handshake with Quickbooks.

https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0#step-4-handle-the-oauth-2-0-server-response
"""
from django.contrib.auth.models import User
from django.db import models
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField

from quickbooks2.get_auth_client import get_auth_client


class UserCredentials(models.Model):
  user = OneToOneOrNoneField(User, on_delete=models.CASCADE)
  code = models.CharField(max_length=100, default='')
  state = models.TextField(default='')
  realmId = models.CharField(max_length=100, default='', help_text=(
      'This is also known as the COMPANY_ID in the python-quickbooks docs'))
  error_response = models.CharField(max_length=100, default='')
  error_description = models.TextField(default='')
  raw_response = models.TextField(default='')

  access_token = models.TextField(default='')
  refresh_token = models.TextField(default='')

  def get_access_and_refresh_tokens(self, protocol_and_host):
    if not self.code or not self.realmId:
      raise Exception(
          'You cant get an access or refresh token if youre missing a code or '
          'realmId, which typically happens when the user declines to grant '
          'the app access.')
    auth_client = get_auth_client(protocol_and_host)
    auth_client.get_bearer_token(self.code, self.realmId)

    self.access_token = auth_client.access_token
    self.refresh_token = auth_client.refresh_token
    self.save()

  def refresh(self, protocol_and_host):
    if not self.refresh_token:
      raise Exception(
          'Youre missing a refresh token, so you cant refresh the access '
          'token.')
    auth_client = get_auth_client(protocol_and_host)
    auth_client.refresh(refresh_token=self.refresh_token)

    # I'm not totally convinced this is correct. The documentation is unclear
    # which of these change when you refresh.
    self.access_token = auth_client.access_token
    self.refresh_token = auth_client.refresh_token
    self.save()
