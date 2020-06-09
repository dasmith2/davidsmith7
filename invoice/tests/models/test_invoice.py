from datetime import date
from djaveDT import to_tz_dt
from djaveTest.unit_test import random_string, get_test_user
from djmoney.money import Money

from invoice.models.invoice import Invoice


def get_test_invoice(**kwargs):
  if 'due' in kwargs:
    raise Exception('due is set automatically on save')
  make_payment_to = 'Make payment to Dave at 43 Dave St., Apt. Dave'
  created_by = kwargs.get('created_by', None)
  if not created_by:
    created_by = get_test_user(**kwargs)
  return Invoice.all.create(
      invoice_id=kwargs.get('invoice_id', 'abc_{}'.format(random_string())),
      make_payment_to=kwargs.get('make_payment_to', make_payment_to),
      created_by=kwargs.get('created_by', created_by),
      sent=to_tz_dt(kwargs.get('sent', None)),
      email_to=kwargs.get('email_to', 'my@client.com'),
      net_days=kwargs.get('net_days', 30),
      paid=to_tz_dt(kwargs.get('paid', None)),
      total=kwargs.get('total', Money(100, 'USD')),
      service_from=kwargs.get('service_from', date(2020, 1, 1)),
      service_to=kwargs.get('service_to', date(2020, 2, 1)))
