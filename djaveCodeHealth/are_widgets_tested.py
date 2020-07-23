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


def test_path_from_widget(widget_path):
  got = re.compile(r'(.*)widgets\/(.*)').search(widget_path)
  if got:
    got = got.groups()
    return '{}tests/widgets/test_{}'.format(got[0], got[1])


def widget_path_from_test(widget_test_path):
  return widget_test_path.replace('tests/', '').replace('test_', '')


def find_widgets():
  return find_widgets_helper(yes_tests=False)


def find_widget_tests():
  return find_widgets_helper(yes_tests=True)


def find_widgets_helper(yes_tests):
  to_return = []
  for (dir_name, d, files) in os.walk('.'):
    if is_widgets_dir(dir_name, yes_tests):
      for file_name in files:
        if file_name not in ['__init__.py']:
          to_return.append(os.path.join(dir_name, file_name))
  return to_return


def is_widgets_dir(dir_name, yes_tests):
  if ignore(dir_name):
    return False
  if re.compile(r'\/widgets$').findall(dir_name):
    is_tests = dir_name.find('tests') >= 0
    return yes_tests == is_tests
  return False


def missing_test_paths():
  to_return = []
  for widget in find_widgets():
    test_path = test_path_from_widget(widget)
    if not os.path.exists(test_path):
      to_return.append(test_path)
  return to_return


def too_many_test_paths():
  to_return = []
  for widget_test in find_widget_tests():
    widget_path = widget_path_from_test(widget_test)
    if not os.path.exists(widget_path):
      to_return.append(widget_test)
  return to_return


def test_path_dir(test_path):
  return re.compile(r'.*widgets').findall(test_path)[0]


def makedirs(test_path):
  try:
    os.makedirs(test_path_dir(test_path))
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
    print(test_path)
    make_test(test_path)
  for test_path in too_many_test_paths():
    print('There\'s no widget for {}'.format(test_path))
