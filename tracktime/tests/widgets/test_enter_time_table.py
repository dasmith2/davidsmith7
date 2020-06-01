from datetime import date

from djaveDT import to_tz_dt
from djaveForm.button import Button
from djaveTable.table import Cell, Row

from tracktime.widgets.enter_time_table import EnterTimeTable
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.tests.widgets.test_case_with_data import TestCaseWithData


class EnterTimeTableTests(TestCaseWithData):
  def setUp(self):
    super().setUp()
    self.setup_user()
    self.setup_projects()
    self.setup_work_sessions()
    self.setup_irrelevant_stuff()

  def test_table_contents(self):
    table = EnterTimeTable(
        self.user, date(2020, 1, 15), None, nnow=to_tz_dt('2020-01-15 15:00'))
    self.assertEqual(['Project', 'Hours: 3.2', ''], table.headers)
    self.assertEqual(3, len(table.rows))

    save_new_row = table.rows[0].cells
    self.assertEqual('project', save_new_row[0].key())
    self.assertEqual(None, save_new_row[0].default)
    self.assertEqual('hours', save_new_row[1].key())
    self.assertEqual('savenew', save_new_row[2].key())

    expected_cells_row_1 = [
        'Project 1', Cell(2.1, classes=['hours']), Button('Delete')]
    expected_row_1 = Row(expected_cells_row_1, pk=self.work_session_2.pk)
    table.rows[1].assertEqual(expected_row_1)

    expected_cells_row_2 = [
        'Project 1', Cell('1.1 starting at 11 a.m.', classes=['hours']),
        Button('Delete')]
    expected_row_2 = Row(expected_cells_row_2, pk=self.work_session_1.pk)
    table.rows[2].assertEqual(expected_row_2)

  def test_save_new(self):
    work_session_count_at_first = ProjectWorkSession.live.count()
    form_data = {'project': self.project_2.pk, 'hours': 3.1, 'savenew': 'yep'}
    table = EnterTimeTable(self.user, date(2020, 1, 15), form_data)
    self.assertEqual(
        work_session_count_at_first + 1, ProjectWorkSession.live.count())

    # The default of the project drop down should reflect the latest project
    save_new_row = table.rows[0]
    self.assertEqual(self.project_2.pk, save_new_row.cells[0].default)

    self.assertEqual(4, len(table.rows))  # Header, 2 existing, 1 new

    first_work_session_row = table.rows[1]
    self.assertEqual('Project 2', first_work_session_row.cells[0])
    self.assertEqual(
        Cell(3.1, classes=['hours']), first_work_session_row.cells[1])
