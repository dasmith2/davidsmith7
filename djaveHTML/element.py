from datetime import datetime, date, timedelta, time

from django.utils.safestring import mark_safe
from djaveDT import tz_dt_to_str, time_to_time_str, d_to_str, tz_dt_to_tz_dt
from djmoney.money import Money


class Element(object):
  def __init__(self, css_classes=None):
    self.css_classes = set()
    if css_classes:
      self.css_classes.update(css_classes)

  def css_class_str(self):
    if self.css_classes:
      return ' class="{}"'.format(' '.join(self.css_classes))
    return ''

  def add_css_class(self, css_class):
    self.css_classes.add(css_class)

  def as_html(self):
    raise NotImplementedError('as_html')

  def as_csv(self):
    raise NotImplementedError('as_csv')

  def __eq__(self, other):
    if isinstance(other, Element):
      return self.as_html() == other.as_html()
    return False


class TagElement(Element):
  def __init__(self, contents, css_classes=None):
    super().__init__(css_classes=css_classes)
    self.contents = contents

  def tag_name(self):
    raise NotImplementedError('tag_name')

  def as_html(self):
    return mark_safe('<{tag_name}{attrs}>{content}</{tag_name}>'.format(
        tag_name=self.tag_name(),
        attrs=self.css_class_str(),
        content=elements_as_html(self.contents)))


class StringElement(Element):
  def __init__(self, the_string):
    super().__init__()
    self.the_string = the_string

  def as_html(self):
    if not self.the_string:
      return '&nbsp;'
    return self.the_string

  def as_csv(self):
    if not self.the_string:
      return ''
    return self.the_string


class ElementList(Element):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  def as_html(self):
    return elements_as_html(self.elements)

  def as_csv(self):
    return elements_as_csv(self.elements)


def assert_elements_equal(
    expected_elements, actual_elements, message_prefix=''):
  if expected_elements.__class__ != actual_elements.__class__:
    raise AssertionError((
        '{}I am expecting cell contents to be of type {}, '
        'but instead it is {}').format(
            message_prefix, expected_elements.__class__,
            actual_elements.__class__))
  if isinstance(expected_elements, list):
    if len(expected_elements) != len(actual_elements):
      raise AssertionError((
          '{}I am expecting {} cell content objects, but I got {} of '
          'them').format(
              message_prefix, len(expected_elements),
              len(actual_elements)))
    for i in range(len(expected_elements)):
      assert_element_equal(
          expected_elements[i], actual_elements[i],
          message_prefix='{} cell content {}'.format(message_prefix, i))
      return True
  return assert_element_equal(
      expected_elements, actual_elements,
      message_prefix=message_prefix)


def assert_element_equal(
    expected_element, actual_element, message_prefix=''):
  if expected_element.__class__ != actual_element.__class__:
    raise AssertionError((
        '{}I am expecting an object of type {} but got an object of '
        'type {}').format(
            message_prefix, expected_element.__class__,
            actual_element.__class__))
  if hasattr(expected_element, 'assertEqual'):
    return expected_element.assertEqual(
        actual_element, message_prefix=message_prefix)
  if expected_element != actual_element:
    raise AssertionError('{}{} != {}'.format(
        message_prefix, expected_element, actual_element))


def elements_as_html(elements):
  to_return = []
  for element in _elements_as_list(elements):
    to_return.append(element.as_html())
  # Don't '\n'.join(to_return) because that will insert whitespace nodes
  # between buttons, causing the buttons to spread out more.
  return ''.join(to_return)


def elements_as_csv(elements):
  to_return = []
  for element in _elements_as_list(elements, csv=True):
    to_return.append(element.as_csv())
  return ''.join(to_return)


def _elements_as_list(elements, csv=False):
  if not isinstance(elements, list):
    return _elements_as_list([elements], csv=csv)
  to_return = []
  for element in elements:
    to_return.append(obj_as_element(element, csv=csv))
  return to_return


def is_primitive(obj):
  return isinstance(obj, (int, str, bool, float))


def obj_as_element(obj, csv=False):
  if isinstance(obj, Element):
    return obj
  if is_primitive(obj):
    if csv:
      return StringElement(str(obj).replace('\n', ' '))
    else:
      return StringElement(str(obj).replace('\n', '<br>'))
  if obj is None:
    return StringElement('')
  if isinstance(obj, datetime):
    if csv:
      return StringElement(tz_dt_to_tz_dt(obj).isoformat())
    else:
      return StringElement(tz_dt_to_str(obj))
  if isinstance(obj, date):
    if csv:
      return StringElement(obj.isoformat())
    else:
      return StringElement(d_to_str(obj))
  if isinstance(obj, timedelta):
    # Trim off microseconds.
    return StringElement(str(timedelta(days=obj.days, seconds=obj.seconds)))
  if isinstance(obj, time):
    return StringElement(time_to_time_str(obj))
  if isinstance(obj, list):
    return ElementList([
        obj_as_element(element) for element in obj])
  if isinstance(obj, Money):
    return StringElement(str(obj))
  raise Exception('I am not sure how to turn a {} into a Element'.format(
      obj.__class__))
