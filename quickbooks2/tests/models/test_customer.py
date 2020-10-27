from collections import namedtuple
from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user

from quickbooks2.models.customer import Customer


QuickBooksCustomer = namedtuple(
    'QuickBooksCustomer', 'Id Active DisplayName SyncToken')


class CustomerTests(TestCase):
  def test_merge_list(self):
    user = get_test_user()

    merge_me = [
        QuickBooksCustomer(1, True, 'Bobs Science Laboratory', '1'),
        QuickBooksCustomer(2, True, 'The Business Woman Hotel', '1')]
    Customer.merge_list(user, merge_me, nnow=to_tz_dt('2020-01-15'))

    self.assertEqual(2, Customer.objects.count())
    Customer.objects.get(
        user=user, qb_id=1, last_synced=to_tz_dt('2020-01-15'), deleted=None,
        name='Bobs Science Laboratory', sync_token='1')
    Customer.objects.get(
        user=user, qb_id=2, last_synced=to_tz_dt('2020-01-15'), deleted=None,
        name='The Business Woman Hotel', sync_token='1')

    merge_me = [
        QuickBooksCustomer(1, False, 'Bobs Bankrupt Science Laboratory', '2'),
        QuickBooksCustomer(2, True, 'The Business Woman Hotel', '1')]
    Customer.merge_list(user, merge_me, nnow=to_tz_dt('2020-01-16'))

    self.assertEqual(2, Customer.objects.count())
    Customer.objects.get(
        user=user, qb_id=1, last_synced=to_tz_dt('2020-01-16'),
        deleted=to_tz_dt('2020-01-16'),
        name='Bobs Bankrupt Science Laboratory', sync_token='2')
    Customer.objects.get(
        user=user, qb_id=2, last_synced=to_tz_dt('2020-01-16'), deleted=None,
        name='The Business Woman Hotel', sync_token='1')
