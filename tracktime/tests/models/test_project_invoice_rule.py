from datetime import date

from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user
from djmoney.money import Money

from tracktime.models.project_invoice_rule import ProjectInvoiceRule
from tracktime.models.project_line_item import (
    project_line_items)
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_project_to_do import get_test_project_to_do
from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.tests.models.test_project_work_session import (
    get_test_project_work_session)


def get_test_project_invoice_rule(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)

  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user(**kwargs)

  sent_to = kwargs.get(
      'sent_to', 'Sent to some client or another, LLC')
  make_payment_to = kwargs.get(
      'make_payment_to', 'Make payment to Dave at 1 Dave St., Apt. Dave')
  default_line_item_description = kwargs.get(
      'default_line_item_description', 'Programming work')
  return ProjectInvoiceRule.objects.create(
      project=project,
      creator=creator,
      hourly_rate=Money(100, 'USD'),
      first_billable_day=kwargs.get('first_billable_day', date(2020, 1, 1)),
      invoice_id_prefix=kwargs.get('invoice_id_prefix', 'abc'),
      sent_to=sent_to,
      make_payment_to=make_payment_to,
      default_line_item_description=default_line_item_description,
      net_days=kwargs.get('net_days', 30))


class CreateInvoiceTests(TestCaseWithData):
  def setUp(self):
    self.setup_everything()
    super().setUp()

  def test_create_invoice(self):
    self.create_invoice()

  def create_invoice(self):
    project_invoice_rule = get_test_project_invoice_rule(
        project=self.project_1, creator=self.user,
        first_billable_day=date(2020, 1, 15))
    invoice = project_invoice_rule.create_invoice(
        nnow=to_tz_dt('2020-02-01 12:00'))
    self.assertTrue(invoice.invoice_id.find('abc') == 0)
    self.assertEqual('Sent to some client or another, LLC', invoice.sent_to)
    self.assertEqual(
        'Make payment to Dave at 1 Dave St., Apt. Dave',
        invoice.make_payment_to)
    self.assertEqual(self.user, invoice.creator)
    self.assertIsNone(invoice.sent)
    self.assertEqual(30, invoice.net_days)
    self.assertIsNone(invoice.due)
    self.assertIsNone(invoice.paid)
    self.assertEqual(Money(320, 'USD'), invoice.total)
    self.assertEqual(date(2020, 1, 15), invoice.service_from)
    self.assertEqual(date(2020, 2, 1), invoice.service_to)

    line_items = project_line_items(invoice)
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
    return invoice

  def test_recreate_invoice(self):
    self.create_invoice().mark_deleted()
    self.create_invoice()


class CreateNothingTests(TestCaseWithData):
  def test_nothing_to_bill_creates_empty_invoice(self):
    self.setup_everything()

    invoice = get_test_project_invoice_rule(
        project=self.project_1, creator=self.user,
        first_billable_day=date(2020, 1, 16)).create_invoice()

    self.assertEqual(Money(0, 'USD'), invoice.total)


class ProjectWorkSessionDupeTests(TestCase):
  def test_dont_put_same_in_2_invoices(self):
    """ One time, I made an invoice with 2 work sessions on the same day, each
    with a few To Dos. Then I "Removed" one of the work sessions and created a
    new invoice. The new invoice sucked in all the To Dos from the day,
    including the ones that had been invoiced already. """
    user = get_test_user()
    project = get_test_project(creator=user)
    get_test_project_work_session(
        user=user, project=project, hours=1, date='2020-01-15',
        started='2020-01-15 11:00', stopped='2020-01-15 12:00')
    get_test_project_to_do(
        creator=user, project=project,
        description='Describe 1', done='2020-01-15 11:30')
    get_test_project_work_session(
        user=user, project=project, hours=1, date='2020-01-15',
        started='2020-01-15 13:00', stopped='2020-01-15 14:00')
    get_test_project_to_do(
        creator=user, project=project,
        description='Describe 2', done='2020-01-15 13:30')

    project_invoice_rule = get_test_project_invoice_rule(
        project=project, creator=user, hourly_rate=Money(100, 'USD'))

    invoice_1 = project_invoice_rule.create_invoice(
        nnow=to_tz_dt('2020-01-15 15:00'))

    self.assertEqual(2, invoice_1.lineitem_set.count())
    li1 = invoice_1.lineitem_set.get(describe_service='Describe 1')
    invoice_1.lineitem_set.get(describe_service='Describe 2')

    li1.mark_deleted(nnow=to_tz_dt('2020-01-15 15:30'))

    invoice_2 = project_invoice_rule.create_invoice(
        nnow=to_tz_dt('2020-01-15 16:00'))
    self.assertEqual(1, invoice_2.lineitem_set.count())
    self.assertEqual(
        'Describe 1', invoice_2.lineitem_set.first().describe_service)
