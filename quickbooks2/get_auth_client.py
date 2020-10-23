""" Return an intuitlib AuthClient, which is useful both for authorization and
for interacting with QuickBooks business objects like Customers and Invoices.
"""
from django.conf import settings
from intuitlib.client import AuthClient

from quickbooks2.get_redirect_url import get_redirect_url


def get_anonymous_auth_client(protocol_and_host):
  """ This works like you'd expect. It doesn't have any side effects. """
  return AuthClient(
      settings.QUICKBOOKS_CLIENT_ID,
      settings.QUICKBOOKS_CLIENT_SECRET,
      get_redirect_url(protocol_and_host),
      settings.QUICKBOOKS_ENVIRONMENT)


def get_authenticated_auth_client_with_new_refresh_token(
    existing_refresh_token, realm_id, protocol_and_host):
  """ According to a thread on the internet, instantiating AuthClient
  sometimes has a side effect of updating the refresh token! So wherever you
  call this function with an existing refresh token, you should then update the
  refresh token. """
  return AuthClient(
      settings.QUICKBOOKS_CLIENT_ID,
      settings.QUICKBOOKS_CLIENT_SECRET,
      get_redirect_url(protocol_and_host),
      settings.QUICKBOOKS_ENVIRONMENT,
      refresh_token=existing_refresh_token,
      realm_id=realm_id)
