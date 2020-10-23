""" Returns a python-quickbooks QuickBooks object that can query and update a
user's data on QuickBooks. """
from quickbooks import QuickBooks


def get_quickbooks_client(user, protocol_and_host):
  user_credentials = user.usercredentials_or_none
  if not user_credentials:
    raise Exception(
        'This user hasnt authorized us on quickbooks yet so I cant create '
        'a quickbooks.QuickBooks, a.k.a. quickbooks_client for them.')
  return get_quickbooks_client_from_credentials(
      user_credentials, protocol_and_host)


def get_quickbooks_client_from_credentials(
    user_credentials, protocol_and_host):
  """ I split this out so that when you do user_credentials.refresh() you can
  just use that user_credentials here instead of having get_quickbooks_client
  re-load the user_credentials from the database and possibly cause a race. """
  auth_client = user_credentials.get_authenticated_auth_client(
      protocol_and_host)
  return QuickBooks(
      auth_client=auth_client, company_id=user_credentials.realmId)
