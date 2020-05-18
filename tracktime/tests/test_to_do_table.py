from djaveDT import str_to_tz_dt
from djaveForm.button import Button
from djaveForm.field import TextAreaField
from djaveTable.table import Row
from djaveTest import TestCase, get_test_user

from tracktime.fields import project_field
from tracktime.models.to_do import ToDo
from tracktime.tables.to_do_table import ToDoTable
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_to_do import get_test_to_do


class ToDoTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.project = get_test_project(name='My rad project')
    self.user = get_test_user()

    # Irrelevant
    get_test_to_do(  # Other user
        description='one', user=get_test_user(), project=self.project)
    get_test_to_do(  # Other project
        description='two', user=self.user, project=get_test_project())
    get_test_to_do(  # Deleted
        description='three', user=self.user, project=self.project,
        deleted=str_to_tz_dt('2020-01-01'))

  def test_empty(self):
    table = ToDoTable(self.user, self.project, None)
    self.assertIsNone(table.headers)
    self.assertEqual(1, len(table.rows))
    table.rows[0].assertEqual(Row([
        TextAreaField('new_description', required=True),
        Button('New to do', button_type='submit')]))

  def test_new_to_do(self):
    to_do_count_before = ToDo.live.count()
    table = ToDoTable(
        self.user, self.project, {
            'new_description': 'Hello world!',
            'newtodo': 'yep'})
    self.assertEqual(2, len(table.rows))
    self.assertEqual(to_do_count_before + 1, ToDo.live.count())
    to_do = ToDo.live.filter(user=self.user, project=self.project).first()
    description = TextAreaField(
        'edit_description', default='Hello world!', required=False)
    buttons = [Button('Save'), Button('Done'), Button('Delete')]
    table.rows[1].assertEqual(Row([
        description, buttons], pk=to_do.pk))

  def test_new_to_do_all_projects(self):
    table = ToDoTable(
        self.user, None, {
            'new_description': 'Hello world!',
            'project': self.project.pk,
            'newtodo': 'yep'})
    to_do = ToDo.live.filter(user=self.user, project=self.project).first()
    description = TextAreaField(
        'edit_description', default='Hello world!', required=False)
    table.rows[0].assertEqual(Row([
        project_field(self.user),
        TextAreaField('new_description', required=True),
        Button('New to do', button_type='submit')]))
    buttons = [Button('Save'), Button('Done'), Button('Delete')]
    table.rows[1].assertEqual(Row(
        ['My rad project', description, buttons], pk=to_do.pk))

  def test_blank_to_do_required(self):
    table = ToDoTable(self.user, self.project, {
        'new_description': '', 'newtodo': 'yep'})
    self.assertEqual(1, len(table.rows))
    expected_description = TextAreaField('new_description', required=True)
    expected_description.set_value('')  # This causes "Required" to show
    table.rows[0].assertEqual(Row([
        expected_description, Button('New to do', button_type='submit')]))
