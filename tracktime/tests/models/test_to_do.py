from datetime import date

from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.to_do import ToDo


def get_test_to_do(**kwargs):
  return set_to_do_stuff(ToDo(), **kwargs)


def set_to_do_stuff(instance, **kwargs):
  if 'user' in kwargs:
    raise Exception('user has been replaced by creator and done_by')
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user(**kwargs)
  instance.description = kwargs.get('description', 'Do some stuff')
  instance.done = to_tz_dt(kwargs.get('done', None))
  instance.deleted = to_tz_dt(kwargs.get('deleted', None))
  instance.creator = creator
  instance.done_by = kwargs.get('done_by', None)
  instance.save()
  if 'created' in kwargs:
    ToDo.live.filter(pk=instance.pk).update(
        created=to_tz_dt(kwargs['created']))
    instance.refresh_from_db()
  return instance


class AllowedTests(TestCase):
  def test_allowed(self):
    user = get_test_user()
    to_do_1 = get_test_to_do(creator=user)
    to_do_2 = get_test_to_do(done_by=user, done='2020-01-15')
    get_test_to_do()  # Other user
    api_key = get_test_user_api_key(user=user)
    expected = set([to_do_1, to_do_2])
    self.assertEqual(expected, set(ToDo.allowed_by_user(user)))
    self.assertEqual(expected, set(ToDo.allowed_by_key(api_key)))
    self.assertEqual(expected, set(api_key.allowed_list(ToDo)))


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


class NotLongDoneTests(TestCase):
  def test_not_long_done(self):
    user = get_test_user()

    not_done = get_test_to_do(creator=user)
    recently_done = get_test_to_do(
        done=to_tz_dt('2020-02-01 11:00'), creator=user, done_by=user)
    # Done a long time ago. Should never show up.
    get_test_to_do(
        done=to_tz_dt('2020-01-01'), creator=user, done_by=user)

    self.assertEqual(
        [not_done, recently_done],
        list(ToDo.live.not_long_done(user, nnow=to_tz_dt('2020-02-01 12:00'))))
