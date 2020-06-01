from djaveForm.button import Button
from djaveForm.field import TextAreaField
from djaveTable.table import Row
from djaveTest import TestCase, get_test_user
from tracktime.fields import project_field
from tracktime.models.project_to_do import ProjectToDo
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_project_to_do import get_test_project_to_do
from tracktime.widgets.project_to_do_table import ProjectToDoTable


class ProjectToDoTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.project = get_test_project(name='My rad project')
    self.user = get_test_user()

    get_test_project_to_do(  # Other project
        description='two', creator=self.user, project=get_test_project())

  def test_new_to_do(self):
    ProjectToDoTable(self.user, self.project, {
        'new_description': 'Hello world!',
        'todo': 'yep'})
    ProjectToDo.live.filter(
        creator=self.user, project_new=self.project,
        description='Hello world!', done__isnull=True).first()

  def test_new_to_do_all_projects(self):
    table = ProjectToDoTable(
        self.user, None, {
            'new_description': 'Hello world!',
            'project': self.project.pk,
            'todo': 'yep'})
    to_do = ProjectToDo.live.filter(
        creator=self.user, project_new=self.project,
        description='Hello world!', done__isnull=True).first()
    description = TextAreaField(
        'edit_description', default='Hello world!', required=False)
    table.rows[0].assertEqual(Row([
        project_field(self.user),
        TextAreaField('new_description', required=True),
        self._to_do_did_buttons()]))
    table.rows[1].assertEqual(Row(
        ['My rad project', description, self._done_delete_buttons()],
        pk=to_do.pk))

  def _done_delete_buttons(self):
    return [Button('Done'), Button('Delete')]

  def _to_do_did_buttons(self):
    return [
        Button('To do', button_type='submit'),
        Button('Did', button_type='submit')]
