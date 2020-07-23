import os
import re
from djaveCodeHealth.ignore import ignore


TEST_TEMPLATE = """from djaveTest.unit_test import TestCase, get_test_user
from {class_path} import {widget_name}


class {widget_name}Tests(TestCase):
  def test_display(self):
    user = get_test_user()
    {lower_widget_name} = {widget_name}(user)
    html = {lower_widget_name}.as_html()
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


def missing_test_paths():
  to_return = []
  for widget in widgets():
    test_path = widget_test_path(widget)
    if not os.path.exists(test_path):
      to_return.append(test_path)
  return to_return


def test_dir(test_path):
  return re.compile(r'.*widgets').findall(test_path)[0]


def makedirs(test_path):
  try:
    os.makedirs(test_dir(test_path))
  except FileExistsError:
    pass


def test_contents(test_path):
  finder = re.compile(r'./(.*)\/tests\/widgets\/test_(.*).py')
  # For instance, ('djaveLogin', 'settings_widget')
  (bottom_dir, lower_widget_name) = finder.findall(test_path)[0]
  class_path = '{}.widgets.{}'.format(bottom_dir, lower_widget_name)
  widget_name = ''.join([
      part.title() for part in lower_widget_name.split('_')])
  return TEST_TEMPLATE.format(
      class_path=class_path, widget_name=widget_name,
      lower_widget_name=lower_widget_name)


def make_test(test_path):
  makedirs(test_path)
  with open(test_path, 'w') as f:
    f.write(test_contents(test_path))


if __name__ == '__main__':
  for test_path in missing_test_paths():
    make_test(test_path)
