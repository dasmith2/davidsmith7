from tracktime.tables.time_breakdown import TimeBreakdown, TimeBreakdownEntry
from tracktime.tests.tables.test_case_with_data import TestCaseWithData


class TimeBreakdownTests(TestCaseWithData):
  def setUp(self):
    super().setUp()

    self.setup_user()
    self.setup_projects()
    self.setup_trackeds()
    self.setup_to_dos()
    self.setup_irrelevant_stuff()

  def test_data_and_display(self):
    request_get = {
        'from_date': '2020-01-15', 'to_date': '2020-01-15',
        'project': self.project_1.pk}
    report = TimeBreakdown(request_get, self.user)
    html = report.as_html()
    report_content = report.time_breakdown_content

    manual_entry = TimeBreakdownEntry('tracked', 'Jan 15, 2020, 2.1 hours')
    punched_entry = TimeBreakdownEntry(
        'tracked', 'Jan 15, 2020, 11 a.m. to 12:06 p.m., 1.1 hours')
    to_do_entry = TimeBreakdownEntry('to_do', self.to_do.description)
    expected_entries = [manual_entry, punched_entry, to_do_entry]
    self.assertEqual(expected_entries, report_content.time_breakdown_entries)
    self.assertTrue(html.find('Jan 15, 2020, 2.1 hours') >= 0)
    self.assertEqual(self.project_1, report_content.project)
    self.assertTrue(html.find(self.project_1.name) >= 0)
    self.assertEqual(3.2, report_content.total)
