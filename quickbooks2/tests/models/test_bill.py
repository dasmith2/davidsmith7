from collections import namedtuple
from djaveClassMagic.get_test_instance import get_test_instance
from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user

from quickbooks2.models.account import Account
from quickbooks2.models.bill import Bill, Line
from quickbooks2.models.vendor import Vendor


class DictToDict:
  def __init__(self, my_dict):
    self.my_dict = my_dict

  def to_dict(self):
    return self.my_dict


QuickBooksBill = namedtuple(
    'QuickBooksBill', 'Id SyncToken APAccountRef Balance VendorRef Line')


QuickBooksLine = namedtuple('QuickBooksLine', 'Id Description Amount')


class BillTests(TestCase):
  def test_merge_list(self):
    user = get_test_user()

    account = get_test_instance(
        Account, user=user, qb_id='222', Name='Accounts Payable')
    vendor = get_test_instance(
        Vendor, user=user, qb_id='123', name='The Business Woman Hotel')

    lines = [QuickBooksLine(33, 'Lumber', 500.5)]
    qb_bill = QuickBooksBill(
        1, '0', DictToDict({'value': '222'}), 500.5,
        DictToDict({'value': '123'}), lines)
    Bill.merge_list(user, [qb_bill], nnow=to_tz_dt('2020-01-15'))

    self.assertEqual(1, Bill.objects.count())
    bill = Bill.objects.get(
        qb_id=1, APAccountRef=account, Balance=500.5, VendorRef=vendor)
    Line.objects.get(qb_id=33, bill=bill, Description='Lumber', Amount=500.5)
