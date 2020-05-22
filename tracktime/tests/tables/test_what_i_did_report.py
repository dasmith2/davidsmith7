from django.shortcuts import reverse
from djaveTable.cell_content import InHref
from djaveTable.table import Row

from tracktime.tables.what_i_did_report import WhatIDidReport
from tracktime.tests.tables.test_case_with_data import TestCaseWithData


class WhatIDidReportTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_work_sessions()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    request_get = {'from_date': '2020-01-15', 'to_date': '2020-01-15'}
    report = WhatIDidReport(request_get, self.user)
    html = report.as_html()
    table = report.what_i_did_content
    self.assertEqual(1, len(table.rows))
    url = reverse('time_breakdown') + (
        '?project={}&from_date=2020-01-15&to_date=2020-01-15'.format(
            self.project_1.pk))
    table.rows[0].assertEqual(Row([self.project_1.name, InHref(3.2, url)]))
