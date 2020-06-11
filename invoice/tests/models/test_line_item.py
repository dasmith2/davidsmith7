from djmoney.money import Money

from invoice.tests.models.test_invoice import get_test_invoice


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
