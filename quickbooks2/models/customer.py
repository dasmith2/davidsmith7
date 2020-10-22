"""

QuickBooks has a concept of Customer. This is our local copy.

from quickbooks2.get_client import get_client
from django.contrib.auth.models import User
from quickbooks.objects.customer import Customer
pah = 'https://davidsmith7-stage.herokuapp.com'
qb_client = get_client(User.objects.first(), pah)
customers = Customer.filter(Active=True, qb=qb_client)

"""

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.models.publishable import Publishable
from djaveDT import now
from quickbooks.objects.customer import Customer as QBCustomer

from quickbooks2.get_quickbooks_client import get_quickbooks_client


def retrieve_all_customers(user, protocol_and_host):
  """ Get and return the list of customers from QuickBooks. """
  qb_client = get_quickbooks_client(user, protocol_and_host)
  return QBCustomer.all(Active=True, qb=qb_client)


def merge_customers(user, quickbooks_customers):
  """ Actually put the given customers in our database.
  quickbooks_customers should be the results of retrieve_customers """
  for qb_customer in quickbooks_customers:
    qb_id = qb_customer.Id
    name = qb_customer_name(qb_customer)
    active = qb_customer.Active

    customer = Customer.allowed_by_user(user).filter(qb_id=qb_id).first()
    if not customer:
      customer = Customer(user=user, qb_id=qb_id)
    customer.name = name
    if active:
      customer.deleted = None
    elif not customer.deleted:
      customer.deleted = now()
    customer.save()


def merge_all_customers(user, protocol_and_host):
  merge_customers(user, retrieve_all_customers(user, protocol_and_host))


def qb_customer_name(qb_customer):
  """ Sometimes they don't have a DisplayName, so, I guess try a bunch
  of other attributes as well. """
  return qb_customer.DisplayName or qb_customer.FullyQualifiedName or (
      qb_customer.PrintOnCheckName or qb_customer.Title or (
          qb_customer.CompanyName or qb_customer.FamilyName))


class Customer(Publishable):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  qb_id = models.PositiveIntegerField()
  name = models.CharField(max_length=200)
  last_synced = models.DateTimeField()

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)
