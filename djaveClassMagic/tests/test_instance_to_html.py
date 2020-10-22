from djaveTest.unit_test import TestCase, get_test_user

from djaveClassMagic.instance_to_html import instance_to_html


class InstanceToHtmlTests(TestCase):
  def test_instance_to_html(self):
    user = get_test_user(username='Dave')
    wrapper = instance_to_html(user)
    self.assertTrue(wrapper.as_html().find('Dave') > 0)
