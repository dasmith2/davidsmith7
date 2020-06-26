from djaveForm.button import Button
from djaveForm.field import TextField
from djaveTable.table import Row
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.project import Project
from tracktime.widgets.projects_table import (
    ArchivedProjectsTable, ProjectsTable, NewProjectNameField)


class ProjectsTableTests(TestCase):
  def test_save_new(self):
    self.user = get_test_user()
    self.assertEqual(0, Project.live.count())
    projects_table = ProjectsTable(self.user, {
        'savenew': 'yep', 'new_name': 'Time Tracker!'})
    self.assertEqual(1, Project.live.count())
    self.project = Project.live.first()
    self.assertEqual(self.user, self.project.creator)

    name_field = NewProjectNameField()
    save_new_button = Button('Save new', button_type='submit')
    projects_table.rows[0].assertEqual(Row([name_field, save_new_button]))

    self.assert_project_row(projects_table.rows[1], 'Archive')
    self.assert_project_row(ProjectsTable(self.user, None).rows[1], 'Archive')

  def test_archive(self):
    self.test_save_new()
    self.assertEqual(2, len(ProjectsTable(self.user, None).rows))
    self.assertEqual(0, len(ArchivedProjectsTable(self.user).rows))
    self.project.mark_deleted()
    self.assertEqual(1, len(ProjectsTable(self.user, None).rows))
    self.assertEqual(1, len(ArchivedProjectsTable(self.user).rows))

    self.assert_project_row(
        ArchivedProjectsTable(self.user).rows[0], 'Un-archive')

  def assert_project_row(self, got_row, archive_action):
    name_field = TextField('edit_name', default='Time Tracker!')
    archive_button = Button(archive_action)
    expected_row = Row(
        [name_field, archive_button], pk=self.project.pk)
    expected_row.assertEqual(got_row)
