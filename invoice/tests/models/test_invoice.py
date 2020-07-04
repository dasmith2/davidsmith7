from datetime import date, datetime
from djaveDT import to_tz_dt, to_d
from djaveTest.unit_test import random_string, get_test_user, TestCase
from djmoney.money import Money

from invoice.models.invoice import (
    Invoice, get_an_invoice_id, CREATED, SENDING, DUE, LATE, PAID)


def get_test_invoice(**kwargs):
  return set_invoice_stuff(Invoice(), **kwargs)


def set_invoice_stuff(invoice, **kwargs):
  if 'due' in kwargs:
    raise Exception('due is set automatically on save')
  sent_to = kwargs.get(
      'sent_to', 'Sent to some client or another, LLC')
  make_payment_to = kwargs.get(
      'make_payment_to', 'Make payment to Dave at 43 Dave St., Apt. Dave')
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user(**kwargs)
  invoice.invoice_id = kwargs.get(
      'invoice_id', 'abc_{}'.format(random_string()))
  invoice.sent_to = sent_to
  invoice.make_payment_to = make_payment_to
  invoice.creator = kwargs.get('creator', creator)
  invoice.sent = to_d(kwargs.get('sent', None))
  if isinstance(invoice.sent, datetime):
    raise Exception('invoice.sent is a date now')
  invoice.net_days = kwargs.get('net_days', 30)
  invoice.paid = to_tz_dt(kwargs.get('paid', None))
  invoice.total = kwargs.get('total', Money(100, 'USD'))
  invoice.service_from = kwargs.get('service_from', date(2020, 1, 1))
  invoice.service_to = kwargs.get('service_to', date(2020, 2, 1))
  invoice.save()
  if 'created' in kwargs:
    Invoice.objects.filter(pk=invoice.pk).update(created=kwargs['created'])
    invoice.refresh_from_db()
  return invoice


class GetAnInvoiceIdTests(TestCase):
  def test_get_an_invoice_id(self):
    self.assertEqual('tt20200101', get_an_invoice_id(
        'tt', nnow=to_tz_dt('2020-01-01 12:00')))
    get_test_invoice(invoice_id='tt20200101')
    self.assertEqual('tt20200101_2', get_an_invoice_id(
        'tt', nnow=to_tz_dt('2020-01-01 12:00')))


class ImportantInvoicesTests(TestCase):
  def test_important_invoices(self):
    user = get_test_user()

    get_test_invoice(  # Paid a while ago
        creator=user, sent=date(2020, 1, 1), paid=to_tz_dt('2020-01-10'))
    recently_paid = get_test_invoice(
        creator=user, sent=date(2020, 1, 1), paid=to_tz_dt('2020-01-15 11:00'))
    past_due = get_test_invoice(
        creator=user, sent=date(2020, 1, 1), net_days=10)
    sent = get_test_invoice(
        creator=user, sent=date(2020, 1, 1))
    new = get_test_invoice(creator=user)
    get_test_invoice()  # Wrong user

    self.assertEqual(
        [new, sent, past_due, recently_paid],
        list(Invoice.live.get_important_invoices(
            user, nnow=to_tz_dt('2020-01-15 12:00'))))


class StatusIfNotPaidTests(TestCase):
  def test_status_if_not_paid(self):
    invoice = get_test_invoice(
        created=to_tz_dt('2020-01-01 12:00'), sent=date(2020, 1, 1),
        paid=to_tz_dt('2020-01-01 12:00'), net_days=10)
    self.assertEqual(
        PAID, invoice.status(nnow=to_tz_dt('2020-01-15 12:00')))
    self.assertEqual(
        LATE, invoice.status_if_not_paid(nnow=to_tz_dt('2020-01-15 12:00')))
    self.assertEqual(
        DUE, invoice.status_if_not_paid(nnow=to_tz_dt('2020-01-05 12:00')))


class GetInvoicesTests(TestCase):
  def test_get_invoices(self):
    user = get_test_user()

    created = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'))
    sending = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'),
        sent=date(2020, 5, 1), net_days=10)
    due = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'),
        sent=date(2020, 1, 5), net_days=10)
    late = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'),
        sent=date(2020, 1, 1), net_days=10)
    paid = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'),
        sent=date(2020, 1, 1), paid=to_tz_dt('2020-01-15 12:00'))

    self.assertFalse(
        Invoice.live.get_invoices(user, created_to=date(2019, 12, 25)))
    self.assertFalse(
        Invoice.live.get_invoices(user, created_from=date(2020, 1, 25)))
    self.assertFalse(Invoice.live.get_invoices(
        get_test_user(), created_from=date(2019, 12, 25),
        created_to=date(2020, 1, 25)))
    self.assertEqual(
        [created, sending, due, late, paid],
        list(Invoice.live.get_invoices(
            user, created_from=date(2019, 12, 25),
            created_to=date(2020, 1, 25))))

    nnow = to_tz_dt('2020-01-15 12:00')
    self.assertEqual([created], list(
        Invoice.live.get_invoices(user, status=CREATED)))
    self.assertEqual([sending], list(
        Invoice.live.get_invoices(user, status=SENDING, nnow=nnow)))
    self.assertEqual([due], list(
        Invoice.live.get_invoices(user, status=DUE, nnow=nnow)))
    self.assertEqual([late], list(
        Invoice.live.get_invoices(user, status=LATE, nnow=nnow)))
    self.assertEqual([paid], list(
        Invoice.live.get_invoices(user, status=PAID)))
