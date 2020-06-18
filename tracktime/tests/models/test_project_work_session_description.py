from datetime import date

from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)
from tracktime.tests.test_case_with_data import TestCaseWithData
from tracktime.tests.models.test_project_line_item import (
    get_test_project_line_item)


class ProjectWorkSessionDescriptionsTests(TestCaseWithData):
  def setUp(self):
    super().setUp()
    self.setup_everything()
    self.line_item = get_test_project_line_item(
        project_work_session=self.work_session_1)

  def test_get_work_sessions(self):
    descriptions = ProjectWorkSessionDescriptions(
        self.project_1, self.user, None, date(2020, 1, 15), 'America/New_York',
        include_invoiced=True)
    self.assertEqual(
        set([self.work_session_1, self.work_session_2]),
        set(list(descriptions.get_work_sessions())))
    self.assertEqual(2, len(descriptions.get_work_session_descriptions()))
    wsds = descriptions.get_work_session_descriptions()
    self.assertEqual(
        set([self.work_session_1, self.work_session_2]),
        set([wsd.work_session for wsd in wsds]))

  def test_get_uninvoiced_work_sessions(self):
    descriptions = ProjectWorkSessionDescriptions(
        self.project_1, self.user, None, date(2020, 1, 15), 'America/New_York',
        include_invoiced=False)
    # So you see, get_work_sessions includes everything regardless of whether
    # it's invoiced.
    self.assertEqual(
        set([self.work_session_1, self.work_session_2]),
        set(list(descriptions.get_work_sessions())))
    # The invoiced work sessions get filtered out in
    # get_work_session_descriptions
    self.assertEqual(1, len(descriptions.get_work_session_descriptions()))
    self.assertEqual(
        self.work_session_2,
        descriptions.get_work_session_descriptions()[0].work_session)

    # Unless the invoice line item is deleted.
    self.line_item.mark_deleted()
    descriptions = ProjectWorkSessionDescriptions(
        self.project_1, self.user, None, date(2020, 1, 15), 'America/New_York',
        include_invoiced=False)
    self.assertEqual(2, len(descriptions.get_work_session_descriptions()))
