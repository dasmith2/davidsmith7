""" Psych! You can't get a quickbooks client directly because refresh tokens
change unexpectedly. Hence, you have to do something more like

from quickbooks.objects.customer import Customer as QBCustomer

def get_all_quickbooks_customers(user, protocol_and_host):
  def actually_get(quickbooks_client):
    QBCustomer.filter(Active=True, qb=quickbooks_client)
  return user.usercredentials.do_query(protocol_and_host, actually_get)
"""
