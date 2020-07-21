from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.project import Project
from tracktime.widgets.project_table import ProjectTable


class ProjectTableTests(TestCase):
  def test_save(self):
    self.user = get_test_user()
    self.assertEqual(0, Project.live.count())
    ProjectTable(self.user, {
        'save': 'yep', 'name': 'Time Tracker!', 'use_clock': 'yep'}, None)
    self.assertEqual(1, Project.live.count())
    project = Project.live.first()
    self.assertEqual('Time Tracker!', project.name)
    self.assertEqual(self.user, project.creator)
    self.assertTrue(project.use_clock)
    self.assertFalse(project.has_to_do_list)

    post = {
        'save': 'yep', 'name': 'Time Tracker?', 'has_to_do_list': 'yep'}
    ProjectTable(self.user, post, project)
    self.assertEqual(1, Project.live.count())
    project.refresh_from_db()
    self.assertEqual('Time Tracker?', project.name)
    self.assertFalse(project.use_clock)
    self.assertTrue(project.has_to_do_list)
