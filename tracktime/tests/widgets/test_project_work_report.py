from datetime import date

from django.shortcuts import reverse
from djaveURL import full_path_as_url_and_query_dict

from tracktime.widgets.project_work_report import (
    ProjectWorkReportContent, project_work_report_url)
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
    self.assertEqual(3.2, report_content.get_total_hours())


class ProjectWorkReportUrlTests(TestCaseWithData):
  def test_project_work_report_url(self):
    self.setup_user()
    self.setup_projects()
    expected_url = reverse('project_work_report') + '?project=' + str(
        self.project_1.pk)
    got_url = project_work_report_url(self.project_1)
    self.assertEqual(
        full_path_as_url_and_query_dict(expected_url),
        full_path_as_url_and_query_dict(got_url))

    expected_url += '&from_date=2020-01-15'
    got_url = project_work_report_url(
        self.project_1, from_date=date(2020, 1, 15))
    self.assertEqual(
        full_path_as_url_and_query_dict(expected_url),
        full_path_as_url_and_query_dict(got_url))
