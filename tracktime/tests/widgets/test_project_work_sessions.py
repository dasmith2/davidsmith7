from djaveTest.unit_test import TestCase, get_test_user
from tracktime.widgets.project_work_sessions import ProjectWorkSessions


class ProjectWorkSessionsTests(TestCase):
  def test_display(self):
    ProjectWorkSessions(get_test_user()).as_html()
