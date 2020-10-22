""" Returns a python-quickbooks QuickBooks object that can query and update a
user's data on QuickBooks. """
from djaveAPI.problem import Problem
from quickbooks import QuickBooks

from quickbooks2.get_auth_client import get_auth_client


def get_quickbooks_client(user, protocol_and_host):
  user_credentials = user.usercredentials_or_none
  if not user_credentials:
    raise Problem(
        'This user hasnt authorized us on quickbooks yet so I cant pull '
        'their list of customers.')
  auth_client = get_auth_client(protocol_and_host)
  return QuickBooks(
      auth_client=auth_client, refresh_token=user_credentials.refresh_token,
      company_id=user_credentials.realmId)
