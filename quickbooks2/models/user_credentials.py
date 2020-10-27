"""
This class is for any state you might want to hold on to as part of doing an
OAuth2.0 handshake with Quickbooks.

https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization/oauth-2.0#step-4-handle-the-oauth-2-0-server-response
"""

import json

from django.contrib.auth.models import User
from django.db import models
from djaveAllowed.models import Allowed
from djaveClassMagic.one_to_one_or_none_field import OneToOneOrNoneField
from djaveDT import now
from intuitlib.exceptions import AuthClientError
from quickbooks import QuickBooks

from quickbooks2.get_auth_client import (
    get_anonymous_auth_client,
    get_authenticated_auth_client_with_new_refresh_token)


class UserCredentials(Allowed):
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
  last_refresh_token = models.TextField(default='')
  refresh_token_updated_at = models.DateTimeField(
      null=True, blank=True,
      help_text='When was the last time the refresh token changed?')
  refresh_reason = models.TextField(default='', help_text=(
      'An explanation of when in the workflow the refresh token was '
      'changed.'))

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)

  def do_query(self, protocol_and_host, query_callback):
    """ query_callback should be a function that takes a single argument:
    a quickbooks.QuickBooks client.

    The whole issue is that when you execute a query against QuickBooks,
    you may simultaneously get a new refresh token. """
    auth_client = self.get_authenticated_auth_client(protocol_and_host)
    quickbooks = QuickBooks(auth_client=auth_client, company_id=self.realmId)
    results = None

    try:
      results = query_callback(quickbooks)
    except AuthClientError as ex:
      if json.loads(ex.content.decode('utf8')) == {
          'error': 'invalid_grant'}:
        self.refresh(protocol_and_host)
        results = query_callback(quickbooks)
      else:
        raise ex
    self.set_refresh_token(
        auth_client.refresh_token, 'Ran a QuickBooks query')

    return results

  def get_authenticated_auth_client(self, protocol_and_host):
    """ My current understanding is that instantiating the auth_client with a
    refresh token sometimes has the totally unexpected, bug-causing side-effect
    of updating the refresh token!

    It's possible I'm wrong and that you don't get a new refresh token until
    after you make a query or something. Stay posted. """
    if not self.refresh_token:
      raise Exception((
          'These user_credentials for {} dont have a refresh_token, '
          'so I cant use them to create an authenticated quickbooks auth '
          'client.').format(self.user))
    if not self.realmId:
      raise Exception((
          'These user_credentials for {} dont have a realmId, '
          'so I cant use them to create an authenticated quickbooks auth '
          'client.').format(self.user))
    auth_client = get_authenticated_auth_client_with_new_refresh_token(
        self.refresh_token, self.realmId, protocol_and_host)
    self.set_refresh_token(
        auth_client.refresh_token,
        'Instantiated the intuitlib.client.AuthClient object')
    return auth_client

  def get_access_and_refresh_tokens(self, protocol_and_host):
    if not self.code or not self.realmId:
      raise Exception(
          'You cant get an access or refresh token if youre missing a code or '
          'realmId, which typically happens when the user declines to grant '
          'the app access.')
    # You obviously don't need an authenticated auth_client in order to get
    # authenticated.
    auth_client = get_anonymous_auth_client(protocol_and_host)
    auth_client.get_bearer_token(self.code, self.realmId)

    self.access_token = auth_client.access_token
    self.set_refresh_token(
        auth_client.refresh_token,
        'Exchanged an access code for a refresh token')

  def set_refresh_token(self, new_refresh_token, reason, clear=False):
    """ If you really want to clear out the refresh token, you have to specify
    clear=True

    reason is an explanation of what just happened that the refresh token may
    have changed. """
    if not new_refresh_token and not clear:
      raise Exception('I just stopped you from clearing the refresh token.')
    if self.refresh_token == new_refresh_token:
      return
    self.last_refresh_token = self.refresh_token
    self.refresh_token = new_refresh_token
    self.refresh_token_updated_at = now()
    self.refresh_reason = reason
    self.save()

  def refresh(self, protocol_and_host):
    if not self.refresh_token:
      raise Exception(
          'Youre missing a refresh token, so you cant refresh the access '
          'token.')
    auth_client = self.get_authenticated_auth_client(protocol_and_host)
    auth_client.refresh()

    # I'm not totally convinced this is correct. The documentation is unclear
    # which of these change when you refresh. Ah, but I think it doesn't matter
    # because it appears access_token is never used.
    self.access_token = auth_client.access_token
    self.set_refresh_token(
        auth_client.refresh_token, 'Explicitly refreshing the refresh token')

  def revoke(self, protocol_and_host):
    if not self.refresh_token:
      raise Exception(
          'Youre missing a refresh token, so you probably cant even access '
          'the api, much less revoke access to the api.')

    auth_client = self.get_authenticated_auth_client(protocol_and_host)
    auth_client.revoke()

    self.access_token = ''
    self.set_refresh_token('', 'Clearing out the refresh token', clear=True)
