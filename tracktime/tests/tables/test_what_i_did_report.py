from django.shortcuts import reverse

from tracktime.tables.what_i_did_report import WhatIDidReport
from tracktime.tests.tables.test_case_with_data import TestCaseWithData


class WhatIDidReportTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_trackeds()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    request_get = {'from_date': '2020-01-15', 'to_date': '2020-01-15'}
    report = WhatIDidReport(request_get, self.user)
    html = report.as_html()
    report_content = report.what_i_did_content

    self.assertEqual(1, len(report_content.projects))
    self.assertEqual(self.project_1.name, report_content.projects[0].name)
    self.assertTrue(html.find(self.project_1.name) >= 0)
    self.assertEqual([self.to_do], report_content.projects[0].to_dos)
    self.assertTrue(html.find(self.to_do.description) >= 0)
    self.assertEqual(3.2, report_content.projects[0].hours)
    self.assertTrue(html.find('3.2') >= 0)
    url = reverse('time_breakdown') + (
        '?project={}&from_date=2020-01-15&to_date=2020-01-15'.format(
            self.project_1.pk))
    self.assertEqual(url, report_content.projects[0].hours_breakdown_url)
    self.assertTrue(html.find(url) >= 0)
