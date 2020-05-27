from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveTest import TestCase, get_test_user

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_work_session import set_work_session_stuff


def get_test_project_work_session(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)

  return set_work_session_stuff(ProjectWorkSession(
      project=project), **kwargs)


class AllowedTests(TestCase):
  def test_allowed(self):
    user = get_test_user()
    work_session = get_test_project_work_session(user=user)
    get_test_project_work_session()  # Different user
    api_key = get_test_user_api_key(user=user)
    self.assertEqual([work_session], list(ProjectWorkSession.allowed(api_key)))
