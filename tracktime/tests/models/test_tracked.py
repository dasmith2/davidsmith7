from datetime import date, timedelta

from djaveTest import TestCase, get_test_user
from djaveDT import str_to_tz_dt, to_tz_dt, to_d

from tracktime.models.tracked import (
    Tracked, DELETED, DONE, ABANDONED, IN_PROGRESS)
from tracktime.tests.models.test_project import get_test_project


def get_test_tracked(**kwargs):
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  started = to_tz_dt(kwargs.get('started', None))
  stopped = to_tz_dt(kwargs.get('stopped', None))
  hours = kwargs.get('hours', None)
  if started and stopped and not hours:
    hours = round((stopped - started).total_seconds() / 3600, 2)
  return Tracked.live.create(
      user=user,
      project=project,
      date=to_d(kwargs.get('date', date(2020, 1, 1))),
      hours=hours,
      started=started,
      stopped=stopped,
      deleted=to_tz_dt(kwargs.get('deleted', None)))


class RunningClockTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user(username='relevant')
    self.project = get_test_project(name='Time Tracker')

    # Irrelevant
    get_test_tracked(  # Really old
        user=self.user, project=self.project, date=date(2020, 1, 1),
        started='2020-01-01 12:00', stopped=None)
    get_test_tracked(  # Clock is stopped
        user=self.user, project=self.project, date=date(2020, 1, 15),
        started='2020-01-15 12:00', stopped='2020-01-15 13:00')
    get_test_tracked(  # Other user
        user=get_test_user(username='irrelevant'), project=self.project,
        date=date(2020, 1, 15), started='2020-01-15 12:00', stopped=None)
    self.deleted = get_test_tracked(  # Canceled
        user=self.user, project=self.project, date=date(2020, 1, 15),
        started='2020-01-15 12:00', deleted='2020-01-15 13:00', stopped=None)

    # Relevant
    self.old = get_test_tracked(
        user=self.user, project=self.project, date=date(2020, 1, 10),
        started='2020-01-10 12:00', stopped=None)
    self.recent = get_test_tracked(
        user=self.user, project=self.project, date=date(2020, 1, 15),
        started='2020-01-15 12:00', stopped=None)

    self.six_pm = str_to_tz_dt('2020-01-15 18:00')

  def test_get_clock_never_stopped(self):
    self.assertEqual(
        [self.old, self.recent], list(Tracked.live.get_clock_never_stopped(
            self.user, nnow=self.six_pm)))

  def test_get_clock_running(self):
    self.assertEqual(
        self.recent, Tracked.live.get_clock_running(
            self.user, nnow=self.six_pm))
    self.recent.deleted = self.recent.started + timedelta(hours=1)
    self.recent.save()
    self.assertIsNone(Tracked.live.get_clock_running(
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
    too_soon_message = (
        'This work session is less than 5 minutes old. You '
        'should probably just cancel it.')
    started_plus_1_minute = self.recent.started + timedelta(minutes=1)
    self.assertEqual(
        too_soon_message,
        self.recent.explain_why_can_not_stop(nnow=started_plus_1_minute))

    # 6pm stuff
    self.assertIsNone(self.recent.explain_why_can_not_stop(nnow=self.six_pm))
    self.assertTrue(self.recent.can_stop(nnow=self.six_pm))
    self.recent.stop(nnow=self.six_pm)
    self.assertEqual(
        'The clock is already stopped on this work session',
        self.recent.explain_why_can_not_stop(nnow=self.six_pm))
    never_started = get_test_tracked(
        user=self.user, project=self.project, date=date(2020, 1, 14))
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
    tracked = get_test_tracked(
        date='2020-01-15',
        started='2020-01-15 12:00')
    self.assertEqual(
        IN_PROGRESS, tracked.status(nnow=str_to_tz_dt('2020-01-15 13:00')))
    self.assertEqual(
        ABANDONED, tracked.status(nnow=str_to_tz_dt('2020-01-17 12:00')))
    tracked.stopped = str_to_tz_dt('2020-01-15 13:00')
    self.assertEqual(DONE, tracked.status())
    tracked.deleted = str_to_tz_dt('2020-01-15 13:00')
    self.assertEqual(DELETED, tracked.status())


class JSONTests(TestCase):
  def test_as_json(self):
    tracked = get_test_tracked(
        date='2020-01-15',
        started='2020-01-15 12:00')
    self.assertEqual(date(2020, 1, 15), tracked.date)
    expected = dict(
        pk=tracked.pk,
        user=tracked.user.pk,
        project=tracked.project.pk,
        date='2020-01-15',
        hours=None,
        started='2020-01-15T12:00:00-05:00',
        stopped=None,
        deleted=None,
        status=ABANDONED)
    self.assertEqual(
        expected, tracked.as_json(nnow=str_to_tz_dt('2020-05-14')))


class PerDayTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    self.fifteenth = get_test_tracked(
        date='2020-01-15', hours=1.0, user=self.user)
    self.sixteenth = get_test_tracked(
        date='2020-01-16', hours=2.0, user=self.user)

    # Irrelevant
    get_test_tracked(
        date='2020-01-13', hours=3.0, user=self.user)  # Wrong day
    get_test_tracked(  # Deleted
        date='2020-01-15', hours=1.0, user=self.user,
        deleted=str_to_tz_dt('2020-01-01'))
    # Wrong user
    get_test_tracked(date='2020-01-15', hours=4.0, user=get_test_user())

  def test_total_hours_per_date(self):
    got = Tracked.live.total_hours_per_date(
        date(2020, 1, 14), date(2020, 1, 17), self.user)
    expected = {
        '2020-01-14': '(0.0 hrs)',
        '2020-01-15': '(1.0 hr)',
        '2020-01-16': '(2.0 hrs)',
        '2020-01-17': '(0.0 hrs)'}
    self.assertEqual(expected, got)

  def test_done_by_user_and_date(self):
    self.assertEqual([self.fifteenth], list(Tracked.live.done_by_user_and_date(
        self.user, date(2020, 1, 15))))
    self.assertEqual(
        set([self.fifteenth, self.sixteenth]),
        set(Tracked.live.done_by_user_and_date_range(
            self.user, date(2020, 1, 15), date(2020, 1, 16))))
