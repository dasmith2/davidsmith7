from django.shortcuts import reverse
from djaveHTML.button import Button
from djaveHTML.a import A
from djaveHTML.table import Row, ButtonsCell
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.tests.models.test_project import get_test_project
from tracktime.widgets.projects_table import (
    ArchivedProjectsTable, ProjectsTable)


class ProjectsTableTests(TestCase):
  def test_archive(self):
    user = get_test_user()
    project = get_test_project(creator=user, name='Time Tracker!')

    # One row is the create new project row.
    self.assertEqual(2, len(ProjectsTable(user).rows))
    self.assertEqual(0, len(ArchivedProjectsTable(user).rows))
    project.mark_deleted()
    self.assertEqual(1, len(ProjectsTable(user).rows))
    self.assertEqual(1, len(ArchivedProjectsTable(user).rows))

    edit_url = reverse('edit_project', kwargs={'pk': project.pk})
    edit_href = A('Edit', edit_url, button=True, classes=['edit'])
    buttons = ButtonsCell([edit_href, Button('Un-archive')])
    expected_row = Row(['Time Tracker!', buttons], pk=project.pk)
    got_row = ArchivedProjectsTable(user).rows[0]
    got_row.assertEqual(expected_row)
