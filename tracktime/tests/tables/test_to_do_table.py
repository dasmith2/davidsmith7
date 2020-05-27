from djaveDT import to_tz_dt
from djaveForm.button import Button
from djaveForm.field import TextAreaField
from djaveTable.table import Row
from djaveTest import TestCase, get_test_user

from tracktime.fields import project_field
from tracktime.models.to_do import ToDo
from tracktime.widgets.to_do_table import ToDoTable
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_to_do import get_test_to_do


class ToDoTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.project = get_test_project(name='My rad project')
    self.user = get_test_user()

    # Irrelevant
    get_test_to_do(  # Other user
        description='one', creator=get_test_user(), project=self.project)
    get_test_to_do(  # Other project
        description='two', creator=self.user, project=get_test_project())
    get_test_to_do(  # Deleted
        description='three', creator=self.user, project=self.project,
        deleted=to_tz_dt('2020-01-01'))

  def test_empty(self):
    table = ToDoTable(self.user, self.project, None)
    self.assertIsNone(table.headers)
    self.assertEqual(1, len(table.rows))
    table.rows[0].assertEqual(Row([
        TextAreaField('new_description', required=True),
        self._to_do_did_buttons()]))

  def test_new_to_do(self):
    to_do_count_before = ToDo.live.count()
    table = ToDoTable(
        self.user, self.project, {
            'new_description': 'Hello world!',
            'todo': 'yep'})
    self.assertEqual(2, len(table.rows))
    self.assertEqual(to_do_count_before + 1, ToDo.live.count())
    to_do = ToDo.live.filter(creator=self.user, project=self.project).first()
    description = TextAreaField(
        'edit_description', default='Hello world!', required=False)
    buttons = [Button('Done'), Button('Delete')]
    table.rows[1].assertEqual(Row([
        description, buttons], pk=to_do.pk))

  def test_did(self):
    table = ToDoTable(
        self.user, self.project, {
            'new_description': 'Hello world!',
            'did': 'yep'}, nnow=to_tz_dt('2020-01-15 12:00'))
    self.assertEqual(1, len(table.rows))
    ToDo.live.get(
        creator=self.user, project=self.project,
        description='Hello world!', done=to_tz_dt('2020-01-15 12:00'),
        done_by=self.user)

  def test_new_to_do_all_projects(self):
    table = ToDoTable(
        self.user, None, {
            'new_description': 'Hello world!',
            'project': self.project.pk,
            'todo': 'yep'})
    to_do = ToDo.live.filter(creator=self.user, project=self.project).first()
    description = TextAreaField(
        'edit_description', default='Hello world!', required=False)
    table.rows[0].assertEqual(Row([
        project_field(self.user),
        TextAreaField('new_description', required=True),
        self._to_do_did_buttons()]))
    buttons = [Button('Done'), Button('Delete')]
    table.rows[1].assertEqual(Row(
        ['My rad project', description, buttons], pk=to_do.pk))

  def test_blank_to_do_required(self):
    table = ToDoTable(self.user, self.project, {
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
