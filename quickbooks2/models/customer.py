""" QuickBooks has a concept of Customer. This is our local copy. """

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable

from quickbooks2.get_client import get_client


def retrieve_customers(user, protocol_and_host):
  """ Get and return the list of customers from QuickBooks. """
  qb_client = get_client(user, protocol_and_host)
  return Customer.all(Active=True, qb=qb_client)


def merge_customers(user, quickbooks_customers):
  """ Actually put the given customers in our database.
  quickbooks_customers should be the results of retrieve_customers """
  for qb_customer in quickbooks_customers:
    pass


class Customer(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)
