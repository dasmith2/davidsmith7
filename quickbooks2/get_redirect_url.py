"""
The redirect url is the url that Quickbooks will send the user back to on our
system after the user consents that we can have access to their data.

Quickbooks finds out about this url because it's in the query string of the url
on Quickbooks we redirect the user to in order to get authorization.
"""
from django.shortcuts import reverse
from djaveURL import strip_trailing_slash


def get_redirect_url(protocol_and_host):
  use_protocol_and_host = strip_trailing_slash(protocol_and_host)

  if not use_protocol_and_host:
    raise Exception(
        'get_redirect_url has to return a complete url, so you '
        'have to say what domain this is on in the protocol_and_host.')
  return '{}{}'.format(use_protocol_and_host, reverse('qb_authorize_callback'))
