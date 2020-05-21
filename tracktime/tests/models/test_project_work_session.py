from datetime import date

from djaveDT import to_tz_dt
from djaveTest import TestCase

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.models.work_session import ABANDONED
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_work_session import set_work_session_stuff


def get_test_project_work_session(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)

  return set_work_session_stuff(ProjectWorkSession(
      project=project), **kwargs)


class JSONTests(TestCase):
  def test_as_json(self):
    work_session = get_test_project_work_session(
        date='2020-01-15',
        started='2020-01-15 12:00')
    self.assertEqual(date(2020, 1, 15), work_session.date)
    expected = dict(
        pk=work_session.pk,
        user=work_session.user.pk,
        date='2020-01-15',
        hours=None,
        started='2020-01-15T12:00:00-05:00',
        stopped=None,
        deleted=None,
        status=ABANDONED,
        project=work_session.project.pk)
    self.assertEqual(
        expected, work_session.as_json(nnow=to_tz_dt('2020-05-14')))
