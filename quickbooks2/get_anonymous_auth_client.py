""" Return an anonymous intuitlib.client.AuthClient which is useful only for
authorization. If you want to get an authenticated AuthClient for querying
QuickBooks data, stop, don't do that, because you stand a good chance of
accidentally invalidating the user's quickbooks credentials. Go take a look at
quickbooks2.models.user_credentials instead. """
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
