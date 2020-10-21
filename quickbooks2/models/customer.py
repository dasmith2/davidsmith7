""" QuickBooks has a concept of Customer. This is our local copy. """

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable

from quickbooks2.get_client import get_client


def retrieve_customers(user, protocol_and_host):
  """ Simply get and return the list of customers from QuickBooks. """
  qb_client = get_client(user, protocol_and_host)
  return Customer.all(Active=True, qb=qb_client)


def merge_customers(user, quickbooks_customers):
  """ merge_customers(user, retrieve_customers(user, protocol_and_host)) """
  for qb_customer in quickbooks_customers:
    pass


class Customer(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)
