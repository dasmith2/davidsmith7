from datetime import date

from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)
from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.tests.models.test_project_invoice_line_item import (
    get_test_project_invoice_line_item)


class ProjectWorkSessionDescriptionsTests(TestCaseWithData):
  def test_get_work_sessions(self):
    self.setup_everything()
    get_test_project_invoice_line_item(
        project_work_session=self.work_session_1)

    descriptions = ProjectWorkSessionDescriptions(
        self.project_1, self.user, None, date(2020, 1, 15), 'America/New_York',
        include_invoiced=True)
    self.assertEqual(
        set([self.work_session_1, self.work_session_2]),
        set(list(descriptions.get_work_sessions())))

    descriptions = ProjectWorkSessionDescriptions(
        self.project_1, self.user, None, date(2020, 1, 15), 'America/New_York',
        include_invoiced=False)
    self.assertEqual(
        [self.work_session_2], list(descriptions.get_work_sessions()))
