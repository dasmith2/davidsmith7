from datetime import date

from djaveAPI.tests.test_user_api_key import get_test_user_api_key
from djaveDT import to_tz_dt
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.models.to_do import ToDo, DONE, NOT_DONE


def get_test_to_do(**kwargs):
  return set_to_do_stuff(ToDo(), **kwargs)


def set_to_do_stuff(instance, **kwargs):
  creator = kwargs.get('creator', None)
  if not creator:
    creator = get_test_user(**kwargs)
  instance.description = kwargs.get('description', 'Do some stuff')
  instance.done = to_tz_dt(kwargs.get('done', None))
  instance.deleted = to_tz_dt(kwargs.get('deleted', None))
  instance.creator = creator
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
    get_test_to_do()  # Other user
    api_key = get_test_user_api_key(user=user)
    expected = [to_do_1]
    self.assertEqual(expected, list(ToDo.allowed_by_user(user)))
    self.assertEqual(expected, list(api_key.allowed_list(ToDo)))


class FilterTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()

    self.not_done = get_test_to_do(
        creator=self.user, created=to_tz_dt('2020-01-09 12:00'),
        description='z')
    self.fifteenth = get_test_to_do(
        creator=self.user, created=to_tz_dt('2020-01-11 12:00'),
        done=to_tz_dt('2020-01-15 12:00'), description='b')
    self.sixteenth = get_test_to_do(
        creator=self.user, created=to_tz_dt('2020-01-12 12:00'),
        done=to_tz_dt('2020-01-16 12:00'), description='c')

    # Irrelevant
    get_test_to_do(  # Other user
        creator=get_test_user(),
        done=to_tz_dt('2020-01-15 12:00'), description='e')

    self.to_dos = ToDo.live.allowed_by_user(self.user)

  def test_filter_not_long_done(self):
    self.assertEqual(set([self.not_done, self.sixteenth]), set(
        ToDo.live.filter_not_long_done(
            self.to_dos, nnow=to_tz_dt('2020-01-17 11:59'))))

  def test_filter_done(self):
    self.assertEqual([self.fifteenth], list(ToDo.live.filter_done(
        self.to_dos, from_dt=to_tz_dt('2020-01-15'),
        to=to_tz_dt('2020-01-15 23:59:59'))))

  def test_filter_created(self):
    self.assertEqual([self.fifteenth], list(ToDo.live.filter_created(
        self.to_dos, from_date=date(2020, 1, 11), to_date=date(2020, 1, 11))))

  def test_filter_status(self):
    self.assertEqual([self.not_done], list(
        ToDo.live.filter_status(self.to_dos, NOT_DONE)))
    self.assertEqual(set([self.fifteenth, self.sixteenth]), set(
        ToDo.live.filter_status(self.to_dos, DONE)))
