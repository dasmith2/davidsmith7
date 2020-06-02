from datetime import date

from djaveDT import to_tz_dt
from djAveJAX import AjaxProblem
from djaveTest import TestCase

from djaveAPI.save import update, save_new
from djaveAPI.tests.models import (
    get_test_my_fake_model, ComplexFakeModel,
    get_test_complex_fake_model)
from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveTest import get_test_user


class SaveTests(TestCase):
  def setUp(self):
    super().setUp()
    user = get_test_user()
    self.other = get_test_my_fake_model(name='Other', user=user)
    self.request_POST = {
        'small_int': 1,
        'large_int': 2,
        'my_date': '2020-05-28',
        'my_date_time': '2020-05-28T12:00:00.000000-04:00',
        'my_char': 'Gourmet surprise',
        'my_text': 'for dinner',
        'my_fake_model': self.other.pk}
    self.user_api_key = get_test_user_api_key(user=user)

  def test_save_new(self):
    instance = save_new(ComplexFakeModel, self.request_POST, self.user_api_key)
    self._test_matches_self_request_POST(instance)
    self.assertTrue(instance.pk > 0)

  def test_block_save_when_violate_max_length(self):
    self.request_POST['my_char'] = '0123456789' * 11
    try:
      save_new(ComplexFakeModel, self.request_POST, self.user_api_key)
    except AjaxProblem as ex:
      expected = (
          'my_char has a maximum length of 100. You sent a string with '
          'length 110')
      self.assertEqual(expected, ex.message)

  def test_update(self):
    instance = get_test_complex_fake_model(save=True)
    self.assertEqual(instance, update(
        instance, self.request_POST, self.user_api_key))
    self._test_matches_self_request_POST(instance)

    instance.refresh_from_db()
    self.assertEqual(1, instance.small_int)

  def _test_matches_self_request_POST(self, instance):
    self.assertEqual(1, instance.small_int)
    self.assertEqual(2, instance.large_int)
    self.assertEqual(date(2020, 5, 28), instance.my_date)
    self.assertEqual(
        to_tz_dt('2020-05-28T12:00:00.000000-04:00'), instance.my_date_time)
    self.assertEqual('Gourmet surprise', instance.my_char)
    self.assertEqual('for dinner', instance.my_text)
    self.assertEqual(self.other, instance.my_fake_model)
