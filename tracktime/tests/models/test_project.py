from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import str_to_tz_dt
from djaveTest.unit_test import get_test_user, TestCase

from tracktime.models.project import Project


def get_test_project(**kwargs):
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user()
  project = Project.live.create(
      name=kwargs.get('name', 'Time Tracker'), creator=creator)
  if 'created' in kwargs:
    created = str_to_tz_dt(kwargs['created'])
    Project.live.filter(pk=project.pk).update(created=created)
    project.refresh_from_db()
  return project


class AllowedTests(TestCase):
  def test_allowed(self):
    user = get_test_user()
    api_key = get_test_user_api_key(user=user)
    project = get_test_project(creator=user)

    get_test_project()  # Different creator

    self.assertEqual([project], list(Project.allowed(api_key)))
