""" QuickBooks has a concept of Customer. This is our local copy. """

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable
from djaveAPI.problem import Problem
from quickbooks import QuickBooks

from quickbooks2.get_auth_client import get_auth_client


def retrieve_customers(user, protocol_and_host):
  """ Simply get and return the list of customers from QuickBooks. """
  user_credentials = user.usercredentials_or_none
  if not user_credentials:
    raise Problem(
        'This user hasnt authorized us on quickbooks yet so I cant pull '
        'their list of customers.')
  auth_client = get_auth_client(protocol_and_host)
  client = QuickBooks(
      auth_client=auth_client, refresh_token=user_credentials.refresh_token,
      company_id=user_credentials.realmId)
  return Customer.all(Active=True, qb=client)


def merge_customers(user, quickbooks_customers):
  """ merge_customers(user, retrieve_customers(user, protocol_and_host)) """
  for qb_customer in quickbooks_customers:
    pass


class Customer(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)
