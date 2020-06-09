from datetime import date

from django.shortcuts import reverse

from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.widgets.project_work_report import (
    project_work_report_url, ProjectWorkReport)


class ProjectWorkReportTests(TestCaseWithData):
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
    report = ProjectWorkReport(request_get, self.user)
    html = report.as_html()
    report_content = report.work_report_content

    self.assertEqual(self.project_1, report_content.project)
    self.assertTrue(html.find(self.project_1.name) >= 0)


class ProjectWorkReportUrlTests(TestCaseWithData):
  def test_project_work_report_url(self):
    self.setup_projects()
    expected_url = reverse('project_work_report') + '?project=' + str(
        self.project_1.pk)
    got_url = project_work_report_url(self.project_1)
    self.assertEqual(expected_url, got_url)

    expected_url += '&from_date=2020-01-15'
    got_url = project_work_report_url(
        self.project_1, from_date=date(2020, 1, 15))
    self.assertEqual(expected_url, got_url)
