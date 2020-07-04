from datetime import date

from djaveDT import to_tz_dt
from djaveForm.button import Button
from djaveForm.field import TextAreaField
from djaveTable.table import Row, Cell
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.to_do import ToDo
from tracktime.widgets.to_dos_table import ToDosTable
from tracktime.tests.models.test_to_do import get_test_to_do


class ToDosTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()

    # Irrelevant
    get_test_to_do(  # Other user
        description='one', creator=get_test_user())
    get_test_to_do(  # Deleted
        description='three', creator=self.user, deleted=to_tz_dt('2020-01-01'))

  def test_empty(self):
    table = ToDosTable(self.user, None)
    table.populate_rows()

    self.assertIsNone(table.headers)
    self.assertEqual(1, len(table.rows))
    table.rows[0].assertEqual(Row([
        TextAreaField('new_description', required=True),
        self._to_do_did_buttons()]))

  def test_new_to_do(self):
    to_do_count_before = ToDo.live.count()

    table = ToDosTable(self.user, {
        'new_description': 'Hello world!',
        'todo': 'yep'})
    table.populate_rows()

    self.assertEqual(2, len(table.rows))
    self.assertEqual(to_do_count_before + 1, ToDo.live.count())
    to_do = ToDo.live.filter(creator=self.user).first()
    description = TextAreaField(
        'description', default='Hello world!', required=False)
    table.rows[1].assertEqual(Row([
        description, Cell(None, classes=['buttons'])], pk=to_do.pk,
        additional_attrs={'data-done': False}))

  def test_did(self):
    table = ToDosTable(self.user, {
        'new_description': 'Hello world!',
        'did': 'yep'}, nnow=to_tz_dt('2020-01-15 12:00'))
    table.populate_rows()

    self.assertEqual(1, len(table.rows))
    ToDo.live.get(
        creator=self.user, description='Hello world!',
        done=to_tz_dt('2020-01-15 12:00'))

  def test_blank_to_do_required(self):
    table = ToDosTable(self.user, {
        'new_description': '', 'todo': 'yep'})
    table.populate_rows()

    self.assertEqual(1, len(table.rows))
    expected_description = TextAreaField('new_description', required=True)
    expected_description.set_value('')  # This causes "Required" to show
    table.rows[0].assertEqual(Row([
        expected_description, self._to_do_did_buttons()]))

  def test_created_from_to(self):
    get_test_to_do(
        description='four', creator=self.user,
        created=to_tz_dt('2019-12-25 12:00'))

    table = ToDosTable(self.user, {})
    table.created_from_date = date(2019, 12, 25)
    table.created_to_date = date(2019, 12, 25)
    table.populate_rows()

    self.assertEqual(2, len(table.rows))

    table = ToDosTable(self.user, {})
    table.created_from_date = date(2020, 1, 1)
    table.created_to_date = date(2020, 1, 1)
    table.populate_rows()

    self.assertEqual(1, len(table.rows))

  def _to_do_did_buttons(self):
    return [
        Button('To do', button_type='submit'),
        Button('Did', button_type='submit')]
