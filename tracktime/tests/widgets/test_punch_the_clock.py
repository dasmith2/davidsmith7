from datetime import date, timedelta, time

from djaveDT import str_to_tz_dt
from djaveHTML.button import Button
from djaveHTML.table import Row
from djaveTest.unit_test import TestCase, get_test_user

from tracktime.widgets.punch_the_clock import PunchTheClock
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.tests.models.test_project import get_test_project


class PunchTheClockTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    self.project_1 = get_test_project(name='Project 1', creator=self.user)
    self.project_2 = get_test_project(
        name='Project 2', creator=self.user, has_to_do_list=False)
    self.project_3 = get_test_project(
        name='Project 3', creator=self.user, use_clock=False)
    self.clicked_start_at = str_to_tz_dt('2020-01-15 11:00')

  def test_not_started_yet(self):
    punch_the_clock = PunchTheClock(
        self.user, date(2020, 1, 15), None, nnow=self.clicked_start_at)
    self._not_started_assertions(punch_the_clock)

  def _not_started_assertions(self, punch_the_clock):
    p1_button = Button(
        'Project 1', key_prefix='startclock', pk=self.project_1.pk,
        button_type='submit')
    p2_button = Button(
        'Project 2', key_prefix='startclock', pk=self.project_2.pk,
        button_type='submit')
    self.assertEqual(
        [p1_button, p2_button], punch_the_clock.content.form_elements)

  def test_punch_in(self):
    a_minute_after_starting = self.clicked_start_at + timedelta(minutes=1)
    self.assertIsNone(ProjectWorkSession.live.get_clock_running(
        self.user, nnow=self.clicked_start_at))

    form_data = {'startclock_{}'.format(self.project_1.pk): 'yep'}
    punch_the_clock = PunchTheClock(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=self.clicked_start_at)

    self.work_session = ProjectWorkSession.live.get_clock_running(
        self.user, nnow=a_minute_after_starting)
    self.assertEqual(self.clicked_start_at, self.work_session.started)
    self.assertEqual(self.project_1, self.work_session.project)

    self._punched_in_assertions(punch_the_clock)
    self._punched_in_assertions(PunchTheClock(
        self.user, date(2020, 1, 15), None, nnow=self.clicked_start_at))

  def _punched_in_assertions(self, punch_the_clock):
    table = punch_the_clock.content.get_table()
    self.assertEqual(['Project', 'Started', ''], table.headers)
    self.assertEqual(1, len(table.rows))
    stop_button = Button('Punch out', button_type='submit')
    cancel_button = Button('Cancel', button_type='submit')
    problem = ''
    expected_row = Row(['Project 1', time(11), [
        stop_button, cancel_button, problem]])
    table.rows[0].assertEqual(expected_row)

  def test_punch_out(self):
    self.test_punch_in()
    form_data = {'punchout': 'yep'}
    punched_out_at = self.clicked_start_at + timedelta(hours=1)
    punch_the_clock = PunchTheClock(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=punched_out_at)
    self.work_session.refresh_from_db()
    self.assertEqual(punched_out_at, self.work_session.stopped)
    self._not_started_assertions(punch_the_clock)

  def test_cancel(self):
    self.test_punch_in()
    form_data = {'cancel': 'yep'}
    canceled_at = self.clicked_start_at + timedelta(minutes=20)

    punch_the_clock = PunchTheClock(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=canceled_at)
    self.work_session.refresh_from_db()
    self.assertEqual(canceled_at, self.work_session.deleted)
    self.assertEqual(None, self.work_session.hours)

    self._not_started_assertions(punch_the_clock)
