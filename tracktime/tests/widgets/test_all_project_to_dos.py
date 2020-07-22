from djaveTest.unit_test import TestCase, get_test_user

from tracktime.widgets.all_project_to_dos import AllProjectToDos
from tracktime.tests.models.test_project_to_do import get_test_project_to_do


class AllProjectToDosTests(TestCase):
  def test_display(self):
    creator = get_test_user()
    to_do = get_test_project_to_do(description='Hello world!', creator=creator)
    report = AllProjectToDos(to_do.project.creator, {}, {})
    self.assertTrue(report.as_html().find('Hello world!') > 0)
