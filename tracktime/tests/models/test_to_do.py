from datetime import date

from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import to_tz_dt
from djaveTest import TestCase, get_test_user

from tracktime.models.to_do import ToDo
from tracktime.tests.models.test_project import get_test_project


def get_test_to_do(**kwargs):
  if 'user' in kwargs:
    raise Exception('user has been replaced by creator and done_by')
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user(**kwargs)
  to_do = ToDo.live.create(
      description=kwargs.get('description', 'Do some stuff'),
      done=to_tz_dt(kwargs.get('done', None)),
      deleted=to_tz_dt(kwargs.get('deleted', None)),
      project=project,
      creator=creator,
      done_by=kwargs.get('done_by', None))
  if 'created' in kwargs:
    ToDo.live.filter(pk=to_do.pk).update(created=to_tz_dt(kwargs['created']))
    to_do.refresh_from_db()
  return to_do


class AllowedTests(TestCase):
  def test_allowed(self):
    user = get_test_user()
    to_do_1 = get_test_to_do(creator=user)
    to_do_2 = get_test_to_do(done_by=user, done='2020-01-15')
    get_test_to_do()  # Other user
    api_key = get_test_user_api_key(user=user)
    self.assertEqual(set([to_do_1, to_do_2]), set(ToDo.allowed(api_key)))


class DoneByUserInDateRangeTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()

    get_test_to_do(
        creator=self.user, done_by=self.user,
        done=to_tz_dt('2020-01-14 12:00'), description='a')
    self.fifteenth = get_test_to_do(
        creator=self.user, done_by=self.user,
        done=to_tz_dt('2020-01-15 12:00'), description='b')
    self.sixteenth = get_test_to_do(
        creator=self.user, done_by=self.user,
        done=to_tz_dt('2020-01-16 12:00'), description='c')
    get_test_to_do(
        creator=self.user, done_by=self.user,
        done=to_tz_dt('2020-01-17 12:00'), description='d')

    # Irrelevant
    get_test_to_do(  # Other user
        creator=get_test_user(), done_by=get_test_user(),
        done=to_tz_dt('2020-01-15 12:00'), description='e')
    get_test_to_do(creator=self.user, description='f')  # Not done

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

    not_done_1 = get_test_to_do(project=project_1, creator=user)
    not_done_2 = get_test_to_do(project=project_2, creator=user)
    # Done. Should never show up.
    get_test_to_do(
        project=project_1, done=to_tz_dt('2020-01-01'), creator=user,
        done_by=user)

    self.assertEqual(
        [not_done_2, not_done_1], list(ToDo.live.not_done(user)))
    self.assertEqual(
        [not_done_1], list(ToDo.live.not_done(user, project_1)))
