from datetime import date

from djaveDT import to_tz_dt
from djaveTest.unit_test import get_test_user
from djmoney.money import Money

from tracktime.models.auto_invoice_config import AutoInvoiceConfig
from tracktime.models.project_invoice_line_item import (
    project_invoice_line_items)
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.test_case_with_data import TestCaseWithData


def get_test_auto_invoice_config(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)

  created_by = kwargs.get('created_by', None)
  if not created_by:
    created_by = get_test_user(**kwargs)

  make_payment_to = kwargs.get(
      'make_payment_to', 'Make payment to Dave at 1 Dave St., Apt. Dave')
  default_line_item_description = kwargs.get(
      'default_line_item_description', 'Programming work')
  return AutoInvoiceConfig.objects.create(
      project=project,
      created_by=created_by,
      hourly_rate=Money(100, 'USD'),
      first_billable_day=kwargs.get('first_billable_day', date(2020, 1, 1)),
      invoice_id_prefix=kwargs.get('invoice_id_prefix', 'abc'),
      make_payment_to=make_payment_to,
      email_to=kwargs.get('email_to', 'email@invoice.to'),
      default_line_item_description=default_line_item_description,
      net_days=kwargs.get('net_days', 30))


class CreateInvoiceTests(TestCaseWithData):
  def test_create_invoice(self):
    self.setup_everything()

    auto_invoice_config = get_test_auto_invoice_config(
        project=self.project_1, created_by=self.user,
        first_billable_day=date(2020, 1, 15))
    invoice = auto_invoice_config.create_invoice(
        nnow=to_tz_dt('2020-02-01 12:00'))
    self.assertTrue(invoice.invoice_id.find('abc') == 0)
    self.assertTrue(len(invoice.invoice_id) == 10)
    self.assertEqual(
        'Make payment to Dave at 1 Dave St., Apt. Dave',
        invoice.make_payment_to)
    self.assertEqual(self.user, invoice.created_by)
    self.assertIsNone(invoice.sent)
    self.assertEqual('email@invoice.to', invoice.email_to)
    self.assertEqual(30, invoice.net_days)
    self.assertIsNone(invoice.due)
    self.assertIsNone(invoice.paid)
    self.assertEqual(Money(320, 'USD'), invoice.total)
    self.assertEqual(date(2020, 1, 15), invoice.service_from)
    self.assertEqual(date(2020, 2, 1), invoice.service_to)

    line_items = project_invoice_line_items(invoice)
    self.assertEqual(2, line_items.count())
    line_items.get(
        project_work_session=self.work_session_1,
        invoice=invoice,
        describe_service='Glue the arms on the manikin',
        amount=Money('110', 'USD'),
        amount_calculation='1.1 hrs * $100.00 / hr')
    line_items.get(
        project_work_session=self.work_session_2,
        invoice=invoice,
        describe_service='Programming work',
        amount=Money('210', 'USD'),
        amount_calculation='2.1 hrs * $100.00 / hr')


class CreateNothingTests(TestCaseWithData):
  def test_nothing_to_bill_no_invoice_created(self):
    self.setup_everything()

    self.assertIsNone(get_test_auto_invoice_config(
        project=self.project_1, user=self.user,
        first_billable_day=date(2020, 1, 16)).create_invoice())
