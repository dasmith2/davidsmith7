from datetime import date

from tracktime.widgets.project_work_report import ProjectWorkReportContent
from tracktime.models.work_session_description import WorkSessionDescription
from tracktime.tests.test_case_with_data import TestCaseWithData


class ProjectWorkReportTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_work_sessions()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    report_content = ProjectWorkReportContent(
        self.user, self.project_1, date(2020, 1, 15), date(2020, 1, 15))
    html = report_content.as_html()

    manual_session = WorkSessionDescription(
        self.work_session_2, 'Jan 15, 2020, 2.1 hours', [])
    punched_session = WorkSessionDescription(
        self.work_session_1, 'Jan 15, 2020, 11 a.m. to 12:06 p.m., 1.1 hours',
        [self.to_do.description])
    expected_sessions = [punched_session, manual_session]
    self.assertEqual(expected_sessions, report_content.get_descriptions())
    self.assertTrue(html.find('Jan 15, 2020, 2.1 hours') >= 0)
    self.assertEqual(3.2, report_content.get_total())
