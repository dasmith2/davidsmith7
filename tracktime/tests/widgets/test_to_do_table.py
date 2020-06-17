from djaveDT import to_tz_dt
from djaveForm.button import Button
from djaveForm.field import TextAreaField
from djaveTable.table import Row, Cell
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.to_do import ToDo
from tracktime.widgets.to_do_table import ToDoTable
from tracktime.tests.models.test_to_do import get_test_to_do


class ToDoTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()

    # Irrelevant
    get_test_to_do(  # Other user
        description='one', creator=get_test_user())
    get_test_to_do(  # Deleted
        description='three', creator=self.user, deleted=to_tz_dt('2020-01-01'))

  def test_empty(self):
    table = ToDoTable(self.user, None)
    self.assertIsNone(table.headers)
    self.assertEqual(1, len(table.rows))
    table.rows[0].assertEqual(Row([
        TextAreaField('new_description', required=True),
        self._to_do_did_buttons()]))

  def test_new_to_do(self):
    to_do_count_before = ToDo.live.count()
    table = ToDoTable(self.user, {
        'new_description': 'Hello world!',
        'todo': 'yep'})
    self.assertEqual(2, len(table.rows))
    self.assertEqual(to_do_count_before + 1, ToDo.live.count())
    to_do = ToDo.live.filter(creator=self.user).first()
    description = TextAreaField(
        'description', default='Hello world!', required=False)
    table.rows[1].assertEqual(Row([
        description, Cell(None, classes=['buttons'])], pk=to_do.pk))

  def test_did(self):
    table = ToDoTable(self.user, {
        'new_description': 'Hello world!',
        'did': 'yep'}, nnow=to_tz_dt('2020-01-15 12:00'))
    self.assertEqual(1, len(table.rows))
    ToDo.live.get(
        creator=self.user, description='Hello world!',
        done=to_tz_dt('2020-01-15 12:00'), done_by=self.user)

  def test_blank_to_do_required(self):
    table = ToDoTable(self.user, {
        'new_description': '', 'todo': 'yep'})
    self.assertEqual(1, len(table.rows))
    expected_description = TextAreaField('new_description', required=True)
    expected_description.set_value('')  # This causes "Required" to show
    table.rows[0].assertEqual(Row([
        expected_description, self._to_do_did_buttons()]))

  def _to_do_did_buttons(self):
    return [
        Button('To do', button_type='submit'),
        Button('Did', button_type='submit')]
