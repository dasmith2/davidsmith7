""" This is an HTML table. It's for displaying things and that's it. Don't get
fancy.  """
from django.utils.safestring import mark_safe
from djaveHTML.element import (
    Element, elements_as_html, elements_as_csv,
    obj_as_element)
from djaveTest.unit_test import recursive_assert_equal


class Table(Element):
  def __init__(
      self, headers=None, rows=None, css_classes=None, title=None, js=None,
      css=None, post_table_buttons=None, **additional_attrs):
    super().__init__(css_classes=css_classes)
    self.headers = headers  # headers can be strings or Cells or nothing.
    self.rows = rows or []
    self.title = title
    self.js = js or ''
    self.css = css
    self.additional_attrs = additional_attrs or {}
    self.post_table_buttons = post_table_buttons or []

  def create_row(
      self, cells=None, css_classes=None, pk=None, **additional_attrs):
    row = Row(cells=cells, css_classes=css_classes, pk=pk, **additional_attrs)
    self.rows.append(row)
    return row

  def write_csv(self, writer):
    header_row = []
    for header in self.headers:
      if isinstance(header, Cell):
        header_row.append(header.as_csv())
      else:
        header_row.append(elements_as_csv(header))
    writer.writerow(header_row)
    for row in self.rows:
      csv_row = []
      for cell in row.cells:
        if isinstance(cell, (Cell, Element)):
          csv_row.append(cell.as_csv())
        else:
          csv_row.append(elements_as_csv(cell))
      writer.writerow(csv_row)

  def as_html(self):
    table_start = []
    for key, value in self.additional_attrs.items():
      table_start.append('{}="{}"'.format(key, value))
    if self.css_classes:
      table_start.append(self.css_class_str())
    table_start_str = '<table>'
    if table_start:
      table_start_str = '<table {}>'.format(' '.join(table_start))

    title = ''
    if self.title:
      title = '<h3>{}</h3>'.format(self.title)

    to_return = [title, table_start_str]

    if self.headers:
      to_return.extend([
          '  <thead>',
          '    <tr>'])
      for header in self.headers:
        if isinstance(header, Cell):
          to_return.append(header.as_html())
        else:
          to_return.append('<th>{}</th>'.format(
              obj_as_element(header).as_html()))
      to_return.extend([
          '    </tr>',
          '  </thead>'])

    to_return.extend(self._rows_html())

    to_return.append('</table>')

    if self.post_table_buttons:
      to_return.append(
          '<div class="margin-top-half post-table-button-wrapper '
          'spread-buttons">')
      for button in self.post_table_buttons:
        to_return.append(button.as_html())
      to_return.append('</div>')

    self._js_or_css_helper('script', self.js, to_return)
    self._js_or_css_helper('style', self.css, to_return)

    return mark_safe('\n'.join(to_return))

  def append_js(self, new_js):
    if not self.js:
      self.js = ''
    self.js = '{}\n{}'.format(self.js, new_js)

  def _js_or_css_helper(self, tag_name, this_content, content_list):
    if this_content:
      open_tag = '<{}>'.format(tag_name)
      close_tag = '</{}>'.format(tag_name)
      if this_content.strip().find(open_tag) != 0:
        content_list.append(
            '{}\n{}\n{}'.format(open_tag, this_content, close_tag))
      else:
        content_list.append(this_content)

  """ I used to do this, but then I found out that __repr__ was getting called
  3 times and __str__ was getting called 1 time, for a total of 4 calls to
  self.as_html per request. I believe this has something to do with template
  rendering. So now you must {{ my_table.as_html }} which correctly does one
  self.as_html per request.

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()
  """

  def _rows_html(self):
    to_return = []
    if self.rows:
      to_return.append('  <tbody>')

      for index, row in enumerate(self.rows):
        css_classes = list(
            row.css_classes | {'row1' if index % 2 == 0 else 'row2'})
        row_start = ['    <tr class="{}"'.format(' '.join(css_classes))]
        for key, value in row.additional_attrs.items():
          row_start.append(' {}="{}"'.format(key, value))
        row_start.append('>')
        to_return.append(''.join(row_start))
        for cell in row.cells:
          use_cell = cell
          if not isinstance(cell, Cell):
            element = cell
            if not isinstance(cell, Element):
              element = obj_as_element(cell)
            use_cell = Cell(element)
          to_return.append(use_cell.as_html())
        to_return.append('    </tr>')
      to_return.append('  </tbody>')
    return to_return


class Cell(Element):
  def __init__(
      self, elements, css_classes=None, is_header=False,
      color=None, none_is_nbsp=True, **additional_attrs):
    super().__init__(css_classes=css_classes)
    """ elements can be a datetime, date, string, float, int, any object
    that inherits from Element, or a list of any of those things. """
    self.elements = elements

    # This just makes sure we populate cells with stuff we can turn into html
    # later. By checking at this point, I prevent garbage in, and make problems
    # much easier to debug.
    obj_as_element(elements)

    self.is_header = is_header
    self.additional_attrs = additional_attrs
    self.color = color
    self.none_is_nbsp = none_is_nbsp

  def as_html(self):
    t_what = 'td'
    if self.is_header:
      t_what = 'th'

    content_str = ''
    if self.none_is_nbsp or self.elements is not None:
      content_str = elements_as_html(self.elements)

    open_tag_parts = [t_what]
    if self.css_classes:
      open_tag_parts.append(self.css_class_str())
    if self.color:
      use_color = self.color
      if use_color[0] != '#':
        use_color = '#{}'.format(use_color)
      open_tag_parts.append('style="background-color: {}"'.format(use_color))
    if self.additional_attrs:
      for (key, value) in self.additional_attrs.items():
        open_tag_parts.append("{}='{}'".format(key, value))
    open_tag_str = ' '.join(filter(None, open_tag_parts))

    return mark_safe(
        '<{}>{}</{}>'.format(open_tag_str, content_str, t_what))

  def as_csv(self):
    return elements_as_csv(self.elements)

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()

  def __eq__(self, other):
    return self.__class__ == other.__class__ and (
        self.as_html() == other.as_html())


class ButtonsCell(Cell):
  def __init__(self, elements=None, **additional_attrs):
    super().__init__(
        elements, css_classes={'buttons'}, none_is_nbsp=False,
        **additional_attrs)


class Row(Element):
  def __init__(
      self, cells=None, css_classes=None, pk=None, **additional_attrs):
    super().__init__(css_classes=css_classes)
    # cells can be primitives, Element objects, or Cells
    self.cells = []
    if cells:
      for cell in cells:
        self.add(cell)
    self.additional_attrs = additional_attrs or {}
    self.pk = pk
    if pk is not None:
      self.additional_attrs['data-pk'] = pk

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    attrs = []
    if self.cells:
      attrs.extend([cell.__repr__() for cell in self.cells])
    if self.css_classes:
      attrs.append('css_classes={}'.format(self.css_classes))
    return 'Row({})'.format(', '.join(attrs))

  def add(self, cell):
    if not isinstance(cell, Cell):
      # This just makes sure we populate cells with stuff we can turn into html
      # later. By checking at this point, I prevent garbage in, and make
      # problems much easier to debug.
      obj_as_element(cell)
    self.cells.append(cell)

  def extend(self, cells):
    for cell in cells:
      self.add(cell)

  def assertEqual(self, expected_row):
    """ Handy for tests. """
    if set(self.css_classes) != set(expected_row.css_classes):
      raise AssertionError(
          'I\'m expecting css_classes {} on this row but I have {}'.format(
              expected_row.css_classes, self.css_classes))
    if self.additional_attrs != expected_row.additional_attrs:
      raise AssertionError((
          'I\'m expecting additional_attrs {} on this row but I '
          'have {}').format(
              expected_row.additional_attrs, self.additional_attrs))
    recursive_assert_equal(expected_row.cells, self.cells, '')
