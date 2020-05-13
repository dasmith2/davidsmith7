from djaveTest import TestCase, get_test_user

from tracktime.tests.models.test_project import get_test_project
from tracktime.models.latest_project import (
    get_latest_project, set_latest_project)


class LatestProjectTests(TestCase):
  def test_get_and_set(self):
    user = get_test_user()
    project_1 = get_test_project(name='Time Tracker')
    project_2 = get_test_project(name='Project Squared Living')

    self.assertIsNone(get_latest_project(user))
    set_latest_project(user, project_1)
    self.assertEqual(project_1, get_latest_project(user))
    set_latest_project(user, project_2)
    self.assertEqual(project_2, get_latest_project(user))
