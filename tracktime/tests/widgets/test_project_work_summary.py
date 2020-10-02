from djaveTest.unit_test import TestCase, get_test_user
from tracktime.widgets.project_work_summary import ProjectWorkSummary


class ProjectWorkSummaryTests(TestCase):
  def test_display(self):
    ProjectWorkSummary(get_test_user()).as_html()
