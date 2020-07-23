from django.shortcuts import reverse
from djaveTest.unit_test import TestCase, get_test_user
from djaveLogin.widgets.settings_widget import SettingsWidget


class SettingsWidgetTests(TestCase):
  def test_display(self):
    user = get_test_user(email='jill@jill.jill')
    settings_widget = SettingsWidget(reverse('to_do'), user)
    html = settings_widget.as_html()
    self.assertTrue(html.find('jill@jill.jill') > 0)
