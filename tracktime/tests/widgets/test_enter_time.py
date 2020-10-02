from datetime import date
from djaveTest.unit_test import TestCase, get_test_user
from tracktime.widgets.enter_time import EnterTime


class EnterTimeTests(TestCase):
  def test_display(self):
    EnterTime(get_test_user(), date.today()).as_html()
