from djaveTest.unit_test import TestCase

from tracktime.tests.models.test_project import get_test_project
from tracktime.widgets.project_to_dos import ProjectToDos


class ProjectToDosTests(TestCase):
  def test_display(self):
    ProjectToDos(get_test_project(), '/whatever').as_html()
