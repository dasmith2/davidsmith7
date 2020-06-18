from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.project_to_do import ProjectToDo
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_to_do import set_to_do_stuff


def get_test_project_to_do(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  return set_to_do_stuff(ProjectToDo(project=project), **kwargs)


class FilterTests(TestCase):
  def test_filter_project(self):
    user = get_test_user()
    project = get_test_project()
    project_to_do = get_test_project_to_do(project=project, creator=user)
    get_test_project_to_do(project=get_test_project(), creator=user)

    to_dos = ProjectToDo.live.allowed_by_user(user)
    self.assertEqual([project_to_do], list(
        ProjectToDo.live.filter_project(to_dos, project)))
