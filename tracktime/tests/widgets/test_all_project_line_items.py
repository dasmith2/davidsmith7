from djaveTest.unit_test import get_test_user, TestCase

from tracktime.widgets.all_project_line_items import AllProjectLineItems


class AllProjectLineItemsTests(TestCase):
  def test_view(self):
    AllProjectLineItems(get_test_user()).as_html()
