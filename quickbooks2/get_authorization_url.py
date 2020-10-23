"""
The authorization url is the url on Quickbooks that you redirect your user to
so they can authorize this here app to access their Quickbooks data. Once
they've done that, quickbooks will redirect them to get_redirect_url(...)

This is all documented at
https://developer.intuit.com/app/developer/qbo/docs/develop/authentication-and-authorization
"""
from intuitlib.enums import Scopes

from quickbooks2.get_auth_client import get_anonymous_auth_client


def get_authorization_url(protocol_and_host):
  scopes = [Scopes.ACCOUNTING]
  return get_anonymous_auth_client(protocol_and_host).get_authorization_url(
      scopes)
