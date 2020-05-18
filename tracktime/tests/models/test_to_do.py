from datetime import date

from djaveTest import TestCase, get_test_user
from djaveDT import to_tz_dt

from tracktime.models.to_do import ToDo, OPEN, DONE
from tracktime.tests.models.test_project import get_test_project


def get_test_to_do(**kwargs):
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  to_do = ToDo.live.create(
      description=kwargs.get('description', 'Do some stuff'),
      done=to_tz_dt(kwargs.get('done', None)),
      deleted=to_tz_dt(kwargs.get('deleted', None)),
      project=project,
      user=user)
  if 'created' in kwargs:
    ToDo.live.filter(pk=to_do.pk).update(created=to_tz_dt(kwargs['created']))
    to_do.refresh_from_db()
  return to_do


class DoneByUserInDateRangeTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()

    get_test_to_do(
        user=self.user, done=to_tz_dt('2020-01-14 12:00'), description='a')
    self.fifteenth = get_test_to_do(
        user=self.user, done=to_tz_dt('2020-01-15 12:00'), description='b')
    self.sixteenth = get_test_to_do(
        user=self.user, done=to_tz_dt('2020-01-16 12:00'), description='c')
    get_test_to_do(
        user=self.user, done=to_tz_dt('2020-01-17 12:00'), description='d')

    # Irrelevant
    get_test_to_do(  # Other user
        user=get_test_user(), done=to_tz_dt('2020-01-15 12:00'),
        description='e')
    get_test_to_do(user=self.user, description='f')  # Not done

  def test_done_by_user_in_date_range(self):
    self.assertEqual(
        set([self.fifteenth, self.sixteenth]),
        set(ToDo.live.done_by_user_in_date_range(
            self.user, date(2020, 1, 15), date(2020, 1, 16))))


class ToDoTests(TestCase):
  def test_not_done(self):
    project_1 = get_test_project(name='Time Tracker')
    project_2 = get_test_project(name='Davespace')
    user = get_test_user()

    not_done_1 = get_test_to_do(project=project_1, user=user)
    not_done_2 = get_test_to_do(project=project_2, user=user)
    # Done. Should never show up.
    get_test_to_do(
        project=project_1, done=to_tz_dt('2020-01-01'), user=user)

    self.assertEqual(
        [not_done_2, not_done_1], list(ToDo.live.not_done(user)))
    self.assertEqual(
        [not_done_1], list(ToDo.live.not_done(user, project_1)))

  def test_as_json(self):
    project = get_test_project()
    user = get_test_user()
    to_do = get_test_to_do(
        description='Hello world', done=None, project=project, user=user,
        created='2020-01-01 13:00')
    expected = dict(
        pk=to_do.pk,
        description='Hello world',
        created='2020-01-01T13:00:00-05:00',
        done=None,
        deleted=None,
        project=project.pk,
        status=OPEN,
        user=user.pk)
    self.assertEqual(expected, to_do.as_json())

    to_do.done = to_tz_dt('2020-01-02 11:00')
    expected['done'] = '2020-01-02T11:00:00-05:00'
    expected['status'] = DONE
    self.assertEqual(expected, to_do.as_json())
