from djaveDT import to_tz_dt
from djaveTest.unit_test import get_test_user, TestCase
from djmoney.money import Money

from invoice.models.line_item import LineItem
from invoice.tests.models.test_invoice import get_test_invoice


def get_test_line_item(**kwargs):
  return set_line_item_stuff(LineItem(), **kwargs)


def set_line_item_stuff(instance, **kwargs):
  invoice = kwargs.get('invoice', None)
  if not invoice:
    invoice = get_test_invoice(**kwargs)
  instance.invoice = invoice
  instance.describe_service = kwargs.get(
      'describe_service', 'I dug a huge hole then filled it back in again.')
  instance.amount = kwargs.get('amount', Money(100, 'USD'))
  instance.amount_calculation = kwargs.get(
      'amount_calculation', '10 hrs * $10 / hr = $100')
  instance.save()
  return instance


class GetLineItemTests(TestCase):
  def test_get_line_items_from_invoices(self):
    user = get_test_user()
    invoice = get_test_invoice(
        creator=user, created=to_tz_dt('2020-01-01 12:00'))
    li_0 = get_test_line_item(invoice=invoice)
    get_test_line_item()
    self.assertEqual([li_0], list(
        LineItem.live.get_line_items_from_invoices([invoice])))
