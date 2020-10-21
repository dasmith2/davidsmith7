""" Return an intuitlib AuthClient, which is useful both for authorization and
for interacting with QuickBooks business objects like Customers and Invoices.
"""
from django.conf import settings
from intuitlib.client import AuthClient

from quickbooks2.get_redirect_url import get_redirect_url


def get_auth_client(protocol_and_host):
  return AuthClient(
      settings.QUICKBOOKS_CLIENT_ID,
      settings.QUICKBOOKS_CLIENT_SECRET,
      get_redirect_url(protocol_and_host),
      settings.QUICKBOOKS_ENVIRONMENT)
