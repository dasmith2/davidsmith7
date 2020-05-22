from datetime import datetime, timedelta, time

from djaveDT import tz_dt_to_str, time_to_time_str


class CellContent(object):
  def as_html(self):
    raise NotImplementedError('as_html')

  def as_csv(self):
    raise NotImplementedError('as_csv')

  def __eq__(self, other):
    return self.as_html() == other.as_html()

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()


class InHref(CellContent):
  def __init__(self, cell_contents, url):
    self.cell_contents = cell_contents
    self.url = url

  def as_html(self):
    return '<a href="{}">{}</a>'.format(
        self.url, cell_contents_as_html(self.cell_contents))

  def as_csv(self):
    return cell_contents_as_csv(self.cell_contents)


class StringContent(CellContent):
  def __init__(self, the_string):
    self.the_string = the_string

  def as_html(self):
    if not self.the_string:
      return '&nbsp;'
    return self.the_string

  def as_csv(self):
    if not self.the_string:
      return ''
    return self.the_string


class Img(CellContent):
  def __init__(self, img_src):
    self.img_src = img_src

  def as_html(self):
    return '<img src="{}" height="100">'.format(self.img_src)

  def as_csv(self):
    return self.img_src


class CellContentList(CellContent):
  def __init__(self, cell_contents):
    self.cell_contents = cell_contents

  def as_html(self):
    return cell_contents_as_html(self.cell_contents)

  def as_csv(self):
    return cell_contents_as_csv(self.cell_contents)


def assert_cell_contents_equal(
    expected_cell_contents, actual_cell_contents, message_prefix=''):
  if expected_cell_contents.__class__ != actual_cell_contents.__class__:
    raise AssertionError((
        '{}I am expecting cell contents to be of type {}, '
        'but instead it is {}').format(
            message_prefix, expected_cell_contents.__class__,
            actual_cell_contents.__class__))
  if isinstance(expected_cell_contents, list):
    if len(expected_cell_contents) != len(actual_cell_contents):
      raise AssertionError((
          '{}I am expecting {} cell content objects, but I got {} of '
          'them').format(
              message_prefix, len(expected_cell_contents),
              len(actual_cell_contents)))
    for i in range(len(expected_cell_contents)):
      assert_cell_content_equal(
          expected_cell_contents[i], actual_cell_contents[i],
          message_prefix='{} cell content {}'.format(message_prefix, i))
      return True
  return assert_cell_content_equal(
      expected_cell_contents, actual_cell_contents,
      message_prefix=message_prefix)


def assert_cell_content_equal(
    expected_cell_content, actual_cell_content, message_prefix=''):
  if expected_cell_content.__class__ != actual_cell_content.__class__:
    raise AssertionError((
        '{}I am expecting an object of type {} but got an object of '
        'type {}').format(
            message_prefix, expected_cell_content.__class__,
            actual_cell_content.__class__))
  if hasattr(expected_cell_content, 'assertEqual'):
    return expected_cell_content.assertEqual(
        actual_cell_content, message_prefix=message_prefix)
  if expected_cell_content != actual_cell_content:
    raise AssertionError('{}{} != {}'.format(
        message_prefix, expected_cell_content, actual_cell_content))


def cell_contents_as_html(cell_contents):
  to_return = []
  for cell_content in _cell_contents_as_list(cell_contents):
    to_return.append(cell_content.as_html())
  return '\n'.join(to_return)


def cell_contents_as_csv(cell_contents):
  to_return = []
  for cell_content in _cell_contents_as_list(cell_contents):
    to_return.append(cell_content.as_csv())
  return ''.join(to_return)


def _cell_contents_as_list(cell_contents):
  if not isinstance(cell_contents, list):
    return _cell_contents_as_list([cell_contents])
  to_return = []
  for cell_content in cell_contents:
    to_return.append(obj_as_cell_content(cell_content))
  return to_return


def is_primitive(obj):
  return isinstance(obj, (int, str, bool, float))


def obj_as_cell_content(obj):
  if isinstance(obj, CellContent):
    return obj
  if is_primitive(obj):
    return StringContent(str(obj))
  if isinstance(obj, datetime):
    return tz_dt_to_str(obj)
  if isinstance(obj, timedelta):
    # Trim off microseconds.
    return str(timedelta(days=obj.days, seconds=obj.seconds))
  if isinstance(obj, time):
    return time_to_time_str(obj)
  if isinstance(obj, list):
    return CellContentList([
        obj_as_cell_content(cell_content) for cell_content in obj])
  raise Exception('I am not sure how to turn a {} into a CellContent'.format(
      obj.__class__))
