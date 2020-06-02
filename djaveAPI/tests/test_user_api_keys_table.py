import re

from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveAPI.widgets.new_user_api_key_table import UserAPIKeysTable
from djaveForm.button import Button
from djaveForm.field import SlugField
from djaveTable.table import Row
from djaveTest import TestCase, get_test_user


class TestUserAPIKeysTable(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    # Different user. Irrelevant.
    get_test_user_api_key()

  def test_nothing_happened_yet(self):
    table = UserAPIKeysTable(self.user, None)
    self.assertEqual(1, len(table.rows))
    expected_row = Row([
        SlugField('username', required=True),
        '',
        Button('Save', button_type='submit')])
    table.rows[0].assertEqual(expected_row)

  def save_new(self):
    request_POST = {'username': 'asdf', 'save': 'yep'}
    return UserAPIKeysTable(self.user, request_POST)

  def test_save_new(self):
    table = self.save_new()
    self.assertEqual(2, len(table.rows))
    user_keys = UserAPIKey.objects.filter(user=self.user)
    self.assertEqual(1, user_keys.count())
    api_key = user_keys.first()

    row = table.rows[1]
    self.assertEqual('asdf', row.cells[0])
    description_tester = re.compile(
        r"Write this down because you'll never see it "
        r"again:<br><br><b>[\w-]{10}")
    self.assertTrue(description_tester.findall(row.cells[1]))
    self.assertEqual(Button('Delete'), row.cells[2])
    self.assertEqual(api_key.pk, row.pk)

  def test_cant_save_dupe_usernames(self):
    for i in range(2):
      self.save_new()
    self.assertEqual(1, UserAPIKey.objects.filter(user=self.user).count())

  def test_cant_save_username_with_space(self):
    request_POST = {'username': 'asdf ', 'save': 'yep'}
    UserAPIKeysTable(self.user, request_POST)
    self.assertEqual(0, UserAPIKey.objects.filter(user=self.user).count())
