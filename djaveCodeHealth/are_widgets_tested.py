import os
import re
from djaveCodeHealth.ignore import ignore


TEST_TEMPLATE = """from djaveTest.unit_test import TestCase
from {class_path} import {widget_name}


class {widget_name}Tests(TestCase):
  def test_display(self):
    {lower_widget_name} = {widget_name}()
    html = {widget_name}.as_html()
    self.assertTrue(html.find('???') > 0)"""


def widget_test_path(widget_path):
  got = re.compile(r'(.*)widgets\/(.*)').search(widget_path)
  if got:
    got = got.groups()
    return '{}tests/widgets/test_{}'.format(got[0], got[1])


def widgets():
  to_return = []
  for (dir_name, d, files) in os.walk('.'):
    if is_widgets_dir(dir_name):
      for file_name in files:
        if file_name not in ['__init__.py']:
          to_return.append(os.path.join(dir_name, file_name))
  return to_return


def is_widgets_dir(dir_name):
  return not ignore(dir_name) and (
      re.compile(r'\/widgets$').findall(dir_name) and (
          dir_name.find('tests') == -1))


def missing():
  to_return = []
  for widget in widgets():
    test_path = widget_test_path(widget)
    if not os.path.exists(test_path):
      to_return.append(test_path)
  return to_return


if __name__ == '__main__':
  print('\n'.join(missing()))
