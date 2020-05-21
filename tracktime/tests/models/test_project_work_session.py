from djaveTest import TestCase

from tracktime.tests.models.test_work_session import get_test_work_session


class ProjectWorkSessionTests(TestCase):
  def test_work_session_save_creates_project_work_session(self):
    # This will go away once the project field is successfully removed from the
    # WorkSession object.
    work_session = get_test_work_session()
    self.assertEqual(
        work_session.project, work_session.projectworksession.project_new)
