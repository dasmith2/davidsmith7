from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_work_session import set_work_session_stuff


def get_test_project_work_session(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)

  return set_work_session_stuff(ProjectWorkSession(
      project=project), **kwargs)
