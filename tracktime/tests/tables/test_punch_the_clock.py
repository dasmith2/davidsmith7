from datetime import date, timedelta, time

from djaveDT import str_to_tz_dt
from djaveForm.button import Button
from djaveTable.table import Row
from djaveTest import TestCase, get_test_user

from tracktime.tables.punch_the_clock import PunchTheClockTable
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.tests.models.test_project import get_test_project


class PunchTheClockTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    self.project_1 = get_test_project(name='Project 1')
    self.project_2 = get_test_project(name='Project 2')
    self.clicked_start_at = str_to_tz_dt('2020-01-15 11:00')

  def test_not_started_yet(self):
    table = PunchTheClockTable(
        self.user, date(2020, 1, 15), nnow=self.clicked_start_at)
    self._not_started_table_assertions(table)

  def _not_started_table_assertions(self, table):
    self.assertEqual(['Project', ''], table.headers)
    self.assertEqual(2, len(table.rows))
    table.rows[0].assertEqual(Row(['Project 1', Button(
        'Start the clock', pk=self.project_1.pk, button_type='submit')]))
    table.rows[1].assertEqual(Row(['Project 2', Button(
        'Start the clock', pk=self.project_2.pk, button_type='submit')]))

  def test_punch_in(self):
    a_minute_after_starting = self.clicked_start_at + timedelta(minutes=1)
    self.assertIsNone(ProjectWorkSession.live.get_clock_running(
        self.user, nnow=a_minute_after_starting))

    form_data = {'starttheclock_{}'.format(self.project_1.pk): 'yep'}
    table = PunchTheClockTable(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=self.clicked_start_at)

    self.work_session = ProjectWorkSession.live.get_clock_running(
        self.user, nnow=a_minute_after_starting)
    self.assertEqual(self.clicked_start_at, self.work_session.started)
    self.assertEqual(self.project_1, self.work_session.project)

    self._punched_in_table_assertions(table)
    self._punched_in_table_assertions(PunchTheClockTable(
        self.user, date(2020, 1, 15), nnow=self.clicked_start_at))

  def _punched_in_table_assertions(self, table):
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
    table = PunchTheClockTable(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=punched_out_at)
    self.work_session.refresh_from_db()
    self.assertEqual(punched_out_at, self.work_session.stopped)
    self._not_started_table_assertions(table)

  def test_cancel(self):
    self.test_punch_in()
    form_data = {'cancel': 'yep'}
    canceled_at = self.clicked_start_at + timedelta(minutes=20)

    table = PunchTheClockTable(
        self.user, date(2020, 1, 15), form_data=form_data,
        nnow=canceled_at)
    self.work_session.refresh_from_db()
    self.assertEqual(canceled_at, self.work_session.deleted)
    self.assertEqual(None, self.work_session.hours)

    self._not_started_table_assertions(table)

  def test_abandoned(self):
    deleted_at = self.clicked_start_at + timedelta(days=1)
    self.assertEqual(date(2020, 1, 16), deleted_at.date())

    self.test_punch_in()
    table = PunchTheClockTable(
        self.user, date(2020, 1, 16), form_data=None, nnow=deleted_at)
    self._abandoned_table_assertions(table)

  def _abandoned_table_assertions(self, table):
    self.assertEqual(['Project', 'Started', ''], table.headers)
    self.assertEqual(3, len(table.rows))
    table.rows[0].assertEqual(Row(['Project 1', '', Button(
        'Start the clock', pk=self.project_1.pk, button_type='submit')]))
    table.rows[1].assertEqual(Row(['Project 2', '', Button(
        'Start the clock', pk=self.project_2.pk, button_type='submit')]))
    delete_button = Button('Abandoned session. Delete.', key_prefix='delete')
    table.rows[2].assertEqual(Row(
        ['Project 1', self.clicked_start_at, delete_button],
        pk=self.work_session.pk))
