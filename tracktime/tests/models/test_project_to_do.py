from djaveTest import TestCase, get_test_user

from tracktime.models.project_to_do import ProjectToDo
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_to_do import set_to_do_stuff


def get_test_project_to_do(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  return set_to_do_stuff(ProjectToDo(project_new=project), **kwargs)


class NotDoneTests(TestCase):
  def test_not_done(self):
    project_1 = get_test_project(name='Time Tracker')
    project_2 = get_test_project(name='Davespace')
    user = get_test_user()

    not_done_1 = get_test_project_to_do(project=project_1, creator=user)
    get_test_project_to_do(project=project_2, creator=user)

    self.assertEqual(
        [not_done_1], list(ProjectToDo.live.not_done(user, project_1)))
