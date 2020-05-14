from datetime import date

from djaveForm.button import Button
from djaveTable.table import Cell, Row
from djaveTest import TestCase, get_test_user

from tracktime.tables.enter_time_table import EnterTimeTable
from tracktime.models.tracked import Tracked
from tracktime.tests.models.test_project import get_test_project
from tracktime.tests.models.test_tracked import get_test_tracked


class EnterTimeTableTests(TestCase):
  def setUp(self):
    super().setUp()
    self.user = get_test_user()
    get_test_user(username='irrelevant_user')
    self.project_1 = get_test_project(name='Project 1')
    self.project_2 = get_test_project(name='Project 2')
    self.tracked_1 = get_test_tracked(
        user=self.user, project=self.project_1, hours=1.1, date='2020-01-15',
        started='2020-01-15 11:00', stopped='2020-01-15 12:06')
    self.tracked_2 = get_test_tracked(
        user=self.user, project=self.project_1, hours=2.1, date='2020-01-15')

    # Irrelevant stuff
    get_test_tracked(  # Wrong day
        user=self.user, project=self.project_1, hours=20.0, date='2020-01-05')
    get_test_tracked(  # Wrong user
        user=get_test_user(), project=self.project_1, hours=30.8,
        date='2020-01-15')
    get_test_tracked(  # Deleted
        user=self.user, project=self.project_1, hours=40.0, date='2020-01-15',
        started='2020-01-15 11:00', stopped='2020-01-15 12:06',
        deleted='2020-01-15 12:08')

  def test_table_contents(self):
    table = EnterTimeTable(self.user, date(2020, 1, 15), None)
    self.assertEqual(['Project', 'Hours: 3.2', ''], table.headers)
    self.assertEqual(3, len(table.rows))

    save_new_row = table.rows[0].cells
    self.assertEqual('project', save_new_row[0].key())
    self.assertEqual(None, save_new_row[0].default)
    self.assertEqual('hours', save_new_row[1].key())
    self.assertEqual('savenew', save_new_row[2].key())

    expected_cells_row_1 = [
        'Project 1', Cell(2.1, classes=['hours']), Button('Delete')]
    expected_row_1 = Row(expected_cells_row_1, pk=self.tracked_2.pk)
    table.rows[1].assertEqual(expected_row_1)

    expected_cells_row_2 = [
        'Project 1', Cell('1.1 starting at 11 a.m.', classes=['hours']),
        Button('Delete')]
    expected_row_2 = Row(expected_cells_row_2, pk=self.tracked_1.pk)
    table.rows[2].assertEqual(expected_row_2)

  def test_save_new(self):
    tracked_count_at_first = Tracked.live.count()
    form_data = {'project': self.project_2.pk, 'hours': 3.1, 'savenew': 'yep'}
    table = EnterTimeTable(self.user, date(2020, 1, 15), form_data)
    self.assertEqual(tracked_count_at_first + 1, Tracked.live.count())

    # The default of the project drop down should reflect the latest project
    save_new_row = table.rows[0]
    self.assertEqual(self.project_2.pk, save_new_row.cells[0].default)

    self.assertEqual(4, len(table.rows))  # Header, 2 existing, 1 new

    first_tracked_row = table.rows[1]
    self.assertEqual('Project 2', first_tracked_row.cells[0])
    self.assertEqual(Cell(3.1, classes=['hours']), first_tracked_row.cells[1])
