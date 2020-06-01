from datetime import date

from tracktime.widgets.work_report import (
    WorkReportContent, WorkSessionDescription)
from tracktime.tests.widgets.test_case_with_data import TestCaseWithData


class WorkReportTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_work_sessions()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    report_content = WorkReportContent(
        self.user, date(2020, 1, 15), date(2020, 1, 15))
    html = report_content.as_html()

    manual_session = WorkSessionDescription('Jan 15, 2020, 2.1 hours', [])
    punched_session = WorkSessionDescription(
        'Jan 15, 2020, 11 a.m. to 12:06 p.m., 1.1 hours',
        [self.to_do.description])
    expected_sessions = [punched_session, manual_session]
    self.assertEqual(
        expected_sessions, report_content.work_session_descriptions)
    self.assertTrue(html.find('Jan 15, 2020, 2.1 hours') >= 0)
    self.assertEqual(3.2, report_content.total)
