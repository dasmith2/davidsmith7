from datetime import date, timedelta

from djaveTest.unit_test import TestCase, get_test_user
from djaveDT import str_to_tz_dt, to_tz_dt, to_d

from tracktime.models.work_session import (
    WorkSession, DELETED, DONE, ABANDONED, IN_PROGRESS)


def get_test_work_session(**kwargs):
  work_session = WorkSession()
  return set_work_session_stuff(work_session, **kwargs)


def set_work_session_stuff(work_session, **kwargs):
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  started = to_tz_dt(kwargs.get('started', None))
  stopped = to_tz_dt(kwargs.get('stopped', None))
  hours = kwargs.get('hours', None)
  if started and stopped and not hours:
    hours = round((stopped - started).total_seconds() / 3600, 2)
  work_session.user = user
  work_session.date = to_d(kwargs.get('date', date(2020, 1, 1)))
  work_session.hours = hours
  work_session.started = started
  work_session.stopped = stopped
  work_session.deleted = to_tz_dt(kwargs.get('deleted', None))
  work_session.save()
  return work_session


class RunningClockTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user(username='relevant')

    # Irrelevant
    get_test_work_session(  # Really old
        user=self.user, date=date(2020, 1, 1),
        started='2020-01-01 12:00', stopped=None)
    get_test_work_session(  # Clock is stopped
        user=self.user, date=date(2020, 1, 15),
        started='2020-01-15 12:00', stopped='2020-01-15 13:00')
    get_test_work_session(  # Other user
        user=get_test_user(username='irrelevant'),
        date=date(2020, 1, 15), started='2020-01-15 12:00', stopped=None)
    self.deleted = get_test_work_session(  # Canceled
        user=self.user, date=date(2020, 1, 15), started='2020-01-15 12:00',
        deleted='2020-01-15 13:00', stopped=None)

    # Relevant
    self.old = get_test_work_session(
        user=self.user, date=date(2020, 1, 10), started='2020-01-10 12:00',
        stopped=None)
    self.recent = get_test_work_session(
        user=self.user, date=date(2020, 1, 15), started='2020-01-15 12:00',
        stopped=None)

    self.six_pm = str_to_tz_dt('2020-01-15 18:00')

  def test_get_clock_never_stopped(self):
    self.assertEqual(
        [self.old, self.recent], list(WorkSession.live.get_clock_never_stopped(
            self.user, nnow=self.six_pm)))

  def test_get_clock_running(self):
    self.assertEqual(
        self.recent, WorkSession.live.get_clock_running(
            self.user, nnow=self.six_pm))
    self.recent.deleted = self.recent.started + timedelta(hours=1)
    self.recent.save()
    self.assertIsNone(WorkSession.live.get_clock_running(
        self.user, nnow=self.six_pm))

  def test_stop_and_clock_running(self):
    self.assertFalse(self.old.clock_running(nnow=self.six_pm))
    try:
      self.old.stop(nnow=self.six_pm)
      self.fail('You shouldnt be able to stop abandoned')
    except Exception as ex:
      self.assertTrue(ex.args[0].find('abandoned') > 0)

    self.assertTrue(self.recent.clock_running(nnow=self.six_pm))

    self.recent.stop(nnow=self.six_pm)
    self.recent.refresh_from_db()

    self.assertFalse(self.recent.clock_running(nnow=self.six_pm))
    self.assertEqual(self.six_pm, self.recent.stopped)
    self.assertEqual(6.0, self.recent.hours)

  def test_abandoned(self):
    self.assertTrue(self.old.abandoned(nnow=self.six_pm))
    self.assertFalse(self.recent.abandoned(nnow=self.six_pm))

    self.old.stopped = self.old.started + timedelta(hours=1)
    self.assertFalse(self.old.abandoned(nnow=self.six_pm))

  def test_explain_why_can_not_stop(self):
    # Earlier stuff
    yesterday = str_to_tz_dt('2020-01-14 18:00')
    self.assertEqual(
        'How can I stop a work session that was started in the future?!',
        self.recent.explain_why_can_not_stop(nnow=yesterday))
    self.assertFalse(self.recent.can_stop(nnow=yesterday))

    # 6pm stuff
    self.assertIsNone(self.recent.explain_why_can_not_stop(nnow=self.six_pm))
    self.assertTrue(self.recent.can_stop(nnow=self.six_pm))
    self.recent.stop(nnow=self.six_pm)
    self.assertEqual(
        'The clock is already stopped on this work session',
        self.recent.explain_why_can_not_stop(nnow=self.six_pm))
    never_started = get_test_work_session(
        user=self.user, date=date(2020, 1, 14), hours=1)
    self.assertEqual(
        'The clock was never started on this work session',
        never_started.explain_why_can_not_stop(nnow=self.six_pm))
    abandoned_message = (
        'This work session appears to be abandoned because it '
        'was started over 16 hours ago')
    self.assertEqual(
        abandoned_message, self.old.explain_why_can_not_stop(nnow=self.six_pm))
    self.assertEqual(
        'This work session was canceled or deleted',
        self.deleted.explain_why_can_not_stop(nnow=self.six_pm))


class StatusTests(TestCase):
  def test_status(self):
    work_session = get_test_work_session(
        date='2020-01-15',
        started='2020-01-15 12:00')
    self.assertEqual(
        IN_PROGRESS,
        work_session.status(nnow=str_to_tz_dt('2020-01-15 13:00')))
    self.assertEqual(
        ABANDONED, work_session.status(nnow=str_to_tz_dt('2020-01-17 12:00')))
    work_session.stopped = str_to_tz_dt('2020-01-15 13:00')
    self.assertEqual(DONE, work_session.status())
    work_session.deleted = str_to_tz_dt('2020-01-15 13:00')
    self.assertEqual(DELETED, work_session.status())


class PerDayTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    self.fifteenth = get_test_work_session(
        date='2020-01-15', hours=1.0, user=self.user)
    self.sixteenth = get_test_work_session(
        date='2020-01-16', hours=2.0, user=self.user)

    # Irrelevant
    get_test_work_session(
        date='2020-01-13', hours=3.0, user=self.user)  # Wrong day
    get_test_work_session(  # Deleted
        date='2020-01-15', hours=1.0, user=self.user,
        deleted=str_to_tz_dt('2020-01-01'))
    # Wrong user
    get_test_work_session(date='2020-01-15', hours=4.0, user=get_test_user())

  def test_total_hours_per_date(self):
    got = WorkSession.live.total_hours_per_date(
        date(2020, 1, 14), date(2020, 1, 17), self.user)
    expected = {
        '2020-01-14': '(0.0 hrs)',
        '2020-01-15': '(1.0 hr)',
        '2020-01-16': '(2.0 hrs)',
        '2020-01-17': '(0.0 hrs)'}
    self.assertEqual(expected, got)

  def test_done_by_user_and_date(self):
    got = list(WorkSession.live.done_by_user_and_date(
        self.user, date(2020, 1, 15)))
    self.assertEqual([self.fifteenth], got)
    self.assertEqual(
        set([self.fifteenth, self.sixteenth]),
        set(WorkSession.live.done_by_user_and_date_range(
            self.user, date(2020, 1, 15), date(2020, 1, 16))))
