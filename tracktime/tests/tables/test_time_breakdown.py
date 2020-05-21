from django.shortcuts import reverse

from tracktime.tables.time_breakdown import (
    TimeBreakdown, WorkSessionDescription, time_breakdown_url)
from tracktime.tests.tables.test_case_with_data import TestCaseWithData


class TimeBreakdownTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_work_sessions()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    request_get = {
        'from_date': '2020-01-15', 'to_date': '2020-01-15',
        'project': self.project_1.pk}
    report = TimeBreakdown(request_get, self.user)
    html = report.as_html()
    report_content = report.time_breakdown_content

    manual_session = WorkSessionDescription('Jan 15, 2020, 2.1 hours', [])
    punched_session = WorkSessionDescription(
        'Jan 15, 2020, 11 a.m. to 12:06 p.m., 1.1 hours',
        [self.to_do.description])
    expected_sessions = [punched_session, manual_session]
    self.assertEqual(
        expected_sessions, report_content.work_session_descriptions)
    self.assertTrue(html.find('Jan 15, 2020, 2.1 hours') >= 0)
    self.assertEqual(self.project_1, report_content.project)
    self.assertTrue(html.find(self.project_1.name) >= 0)
    self.assertEqual(3.2, report_content.total)


class TimeBreakdownUrlTests(TestCaseWithData):
  def test_time_breakdown_url(self):
    self.setup_projects()
    expected_url = reverse('report') + '?project=' + str(self.project_1.pk)
    got_url = time_breakdown_url(self.project_1)
    self.assertEqual(expected_url, got_url)
