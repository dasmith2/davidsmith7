from datetime import date, timedelta

from djaveTest import TestCase, get_test_user
from djaveDT import str_to_tz_dt, to_tz_dt, to_d

from tracktime.models.tracked import Tracked
from tracktime.tests.models.test_project import get_test_project


def get_test_tracked(**kwargs):
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  project = kwargs.get('project', None)
  if not project:
    project = get_test_project(**kwargs)
  return Tracked.objects.create(
      user=user,
      project=project,
      date=to_d(kwargs.get('date', date(2020, 1, 1))),
      hours=kwargs.get('hours', 1),
      started=to_tz_dt(kwargs.get('started', None)),
      stopped=to_tz_dt(kwargs.get('stopped', None)))


class RunningClockTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user(username='relevant')
    self.project = get_test_project(name='Time Tracker')

    self.old = get_test_tracked(
        user=self.user, project=self.project, date=date(2020, 1, 10),
        started='2020-01-10 12:00', stopped=None)
    self.recent = get_test_tracked(
        user=self.user, project=self.project, date=date(2020, 1, 15),
        started='2020-01-15 12:00', stopped=None)

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

    self.six_pm = str_to_tz_dt('2020-01-15 18:00')

  def test_get_clock_never_stopped(self):
    self.assertEqual(
        [self.old, self.recent], list(Tracked.objects.get_clock_never_stopped(
            self.user, nnow=self.six_pm)))

  def test_get_clock_running(self):
    self.assertEqual(
        self.recent, Tracked.objects.get_clock_running(
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


class JSONTests(TestCase):
  def test_as_json(self):
    tracked = get_test_tracked(
        date='2020-01-15',
        hours=2.0,
        started='2020-01-15 12:00')
    self.assertEqual(date(2020, 1, 15), tracked.date)
    expected = dict(
        pk=tracked.pk,
        user=tracked.user.pk,
        project=tracked.project.pk,
        date='2020-01-15',
        hours=2.0,
        started='2020-01-15T12:00:00-05:00',
        stopped=None)
    self.assertEqual(expected, tracked.as_json())


class TotalHoursPerDayTests(TestCase):
  def test_total_hours_per_day(self):
    user = get_test_user()
    get_test_tracked(date='2020-01-15', hours=1.0, user=user)
    get_test_tracked(date='2020-01-16', hours=2.0, user=user)

    # Irrelevant
    get_test_tracked(date='2020-01-15', hours=0.0, user=user)  # No hours
    get_test_tracked(date='2020-01-13', hours=3.0, user=user)  # Wrong day
    # Wrong user
    get_test_tracked(date='2020-01-15', hours=4.0, user=get_test_user())

    got = Tracked.objects.total_hours_per_day(
        date(2020, 1, 14), date(2020, 1, 17), user)
    expected = {
        '2020-01-14': '(0.0 hrs)',
        '2020-01-15': '(1.0 hr)',
        '2020-01-16': '(2.0 hrs)',
        '2020-01-17': '(0.0 hrs)'}
    self.assertEqual(expected, got)
