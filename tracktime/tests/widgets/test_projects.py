from djaveTest.unit_test import TestCase
from tracktime.widgets.projects import Projects


class ProjectsTests(TestCase):
  def test_display(self):
    Projects().as_html()
