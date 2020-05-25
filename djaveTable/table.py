from django.utils.safestring import mark_safe
from djaveTable.csv import csv_writer_and_response
from djaveTable.cell_content import (
    CellContent, cell_contents_as_html, cell_contents_as_csv,
    obj_as_cell_content)
from djaveTest import recursive_assert_equal


class Table(object):
  def __init__(
      self, headers=None, rows=None, classes=[],
      title=None):
    self.headers = headers  # headers can be strings or Cells or nothing.
    self.rows = rows or []
    self.classes = classes
    self.title = title

  def create_row(
      self, cells=None, additional_attrs=None, classes=None, pk=None):
    row = Row(
        cells=cells, additional_attrs=additional_attrs, classes=classes,
        pk=pk)
    self.rows.append(row)
    return row

  def csv_response(self, file_name):
    writer, response = csv_writer_and_response(file_name)
    header_row = []
    for header in self.headers:
      if isinstance(header, Cell):
        header_row.append(header.as_csv())
      else:
        header_row.append(header)
    writer.writerow(header_row)
    for row in self.rows:
      csv_row = []
      for cell in row.cells:
        if isinstance(cell, [Cell, CellContent]):
          csv_row.append(cell.as_csv())
        else:
          csv_row.append(cell)
      writer.writerow(csv_row)
    return response

  def as_html(self):
    classes_str = ''
    if self.classes:
      classes_str = ' class="{}"'.format(' '.join(self.classes))
    title = ''
    if self.title:
      title = '<h3>{}</h3>'.format(self.title)
    to_return = [title, '<table{}>'.format(classes_str)]
    if self.headers:
      to_return.extend([
          '  <thead>',
          '    <tr>'])
      for header in self.headers:
        if isinstance(header, (Cell, CellContent)):
          to_return.append(header.as_html())
        else:
          to_return.append('<th>{}</th>'.format(header))
      to_return.extend([
          '    </tr>',
          '  </thead>'])

    to_return.extend(self._rows_html())

    to_return.append('</table>')
    return mark_safe('\n'.join(to_return))

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()

  def _rows_html(self):
    to_return = []
    if self.rows:
      to_return.append('  <tbody>')

      for index, row in enumerate(self.rows):
        classes = row.classes + ['row1' if index % 2 == 0 else 'row2']
        row_start = ['    <tr class="{}"'.format(' '.join(classes))]
        for key, value in row.additional_attrs.items():
          row_start.append(' {}="{}"'.format(key, value))
        row_start.append('>')
        to_return.append(''.join(row_start))
        for cell in row.cells:
          use_cell = cell
          if not isinstance(cell, Cell):
            cell_content = cell
            if not isinstance(cell, CellContent):
              cell_content = obj_as_cell_content(cell)
            use_cell = Cell(cell_content)
          to_return.append(use_cell.as_html())
        to_return.append('    </tr>')
      to_return.append('  </tbody>')
    return to_return


class Cell(object):
  def __init__(
      self, cell_contents, classes=[], is_header=False,
      additional_attrs=None, color=None):
    """ cell_contents can be a datetime, date, string, float, int, any object
    that inherits from CellContent, or a list of any of those things. """
    self.cell_contents = cell_contents
    self.classes = classes
    self.is_header = is_header
    self.additional_attrs = additional_attrs
    self.color = color

  def as_html(self):
    t_what = 'td'
    if self.is_header:
      t_what = 'th'
    content_str = cell_contents_as_html(self.cell_contents)

    open_tag_parts = [t_what]
    if self.classes:
      open_tag_parts.append('class="{}"'.format(' '.join(self.classes)))
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
    return cell_contents_as_csv(self.cell_contents)

  def __str__(self):
    return self.as_html()

  def __repr__(self):
    return self.as_html()

  def __eq__(self, other):
    return self.__class__ == other.__class__ and (
        self.as_html() == other.as_html())


class Row(object):
  def __init__(self, cells=None, classes=None, additional_attrs=None, pk=None):
    # cells can be primitives, CellContent objects, or Cells
    self.cells = cells or []
    self.classes = classes or []
    self.additional_attrs = additional_attrs or {}
    if pk is not None:
      self.additional_attrs['data-pk'] = pk

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    attrs = []
    if self.cells:
      attrs.extend([cell.__repr__() for cell in self.cells])
    if self.classes:
      attrs.append('classes={}'.format(self.classes))
    return 'Row({})'.format(', '.join(attrs))

  def add(self, cell):
    self.cells.append(cell)

  def extend(self, cells):
    self.cells.extend(cells)

  def add_class(self, css_class):
    self.classes.append(css_class)

  def assertEqual(self, expected_row):
    """ Handy for tests. """
    if set(self.classes) != set(expected_row.classes):
      raise AssertionError(
          'I\'m expecting classes {} on this row but I have {}'.format(
              expected_row.classes, self.classes))
    if self.additional_attrs != expected_row.additional_attrs:
      raise AssertionError((
          'I\'m expecting additional_attrs {} on this row but I '
          'have {}').format(
              expected_row.additional_attrs, self.additional_attrs))
    recursive_assert_equal(expected_row.cells, self.cells, '')
