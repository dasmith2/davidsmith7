from djaveTest.unit_test import TestCase
from djavError.widgets.trigger_errors import TriggerErrors


class TriggerErrorsTests(TestCase):
  def test_display(self):
    html = TriggerErrors(None, {}).as_html()
    self.assertTrue(html.find('Trigger server error') > 0)
    try:
      TriggerErrors(None, {'triggerservererror': 'yep'})
      self.fail('This should trigger an error')
    except Exception:
      pass
