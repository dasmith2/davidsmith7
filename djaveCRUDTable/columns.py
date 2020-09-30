from django.utils.safestring import mark_safe
from djaveClassMagic.cases import lower_case_plural
from djaveClassMagic.default_widget import default_widget
from djaveClassMagic.model_fields import model_fields
from djaveHTML.a import AButton
from djaveHTML.button import Button


class DisplayColumn(object):
  """ This is an abstract base class. You probably want to use
  DisplayFieldColumn, EditFieldColumn, or ButtonsColumn or make your own type
  of column. """
  def __init__(self, header, cell_template, header_css_class=None):
    self.header = header
    self.cell_template = cell_template
    self.header_css_class = header_css_class

  def inline_create_cell(self):
    # Meaning, the inline create cell is the same as the regular cells
    return self.cell_template

  def safe_inline_create_cell(self):
    """ This is ultimately what crud_table.html calls to render the cell for
    this column that goes in the inline-create-row """
    return mark_safe(self.inline_create_cell())

  def td_around(self, td_css_class, content):
    return mark_safe('<td class="{}">{}</td>'.format(td_css_class, content))

  def default_inline_create_cell_with_widget(self, model, field_name):
    field = model_fields(model, specific_field=field_name)
    widget = default_widget(field)
    return self.td_around(field_name, widget.as_html())

  def header_contents(self):
    if isinstance(self.header, str):
      return self.header
    return self.header.as_html()


class EditFieldColumn(DisplayColumn):
  """ The inline-create-cell and the regular rows all have the default widget
  to edit this field. """
  def __init__(self, model, field_name):
    field = model_fields(model, specific_field=field_name)
    cell_template = self.default_inline_create_cell_with_widget(
        model, field_name)
    super().__init__(field.display_name, cell_template)


class DisplayFieldColumn(DisplayColumn):
  """ The inline-create-cell has the default widget to edit this field, but the
  regular rows simply display the field. The model argument is only necessary
  if you allow inline create. """
  def __init__(
      self, header, field_name=None, header_css_class=None,
      cell_css_class=None, model=None):

    self.field_name = field_name or header.lower()
    self.model = model

    _cell_css_class = self.field_name
    if cell_css_class:
      _cell_css_class += ' {}'.format(cell_css_class)
    cell_template = self.td_around(
        _cell_css_class, self.template_template().format(self.field_name))
    super().__init__(header, cell_template, header_css_class)

  def template_template(self):
    return '<%= {} %>'

  def inline_create_cell(self):
    if not self.model:
      raise Exception(
          'In order to automatically create the inline_create_cell, I need to '
          'know what model this column is for, so you have to pass it in the '
          'constructor.')
    return self.default_inline_create_cell_with_widget(
        self.model, self.field_name)


class ReadonlyFieldColumn(DisplayFieldColumn):
  """ In this case, field_name doesn't actually have to be
  a field of the object. It simply needs to be present in the object's json, so
  you can add it in the model with def add_to_json. """
  def inline_create_cell(self):
    return self.td_around('', '')


class DisplayMoneyColumn(DisplayFieldColumn):
  def template_template(self):
    return '$<%= {} %>'


class ButtonsColumn(DisplayColumn):
  def __init__(self, buttons):
    self.buttons = buttons
    super().__init__(self.buttons_header(), self.cell_template())

  def buttons_header(self):
    return mark_safe('&nbsp;')

  def cell_template(self):
    return self.buttons_cell(self.buttons)

  def buttons_cell(self, buttons):
    if buttons:
      buttons[-1].add_css_class('last-button')
    button_str = ''.join([button.as_html() for button in buttons])
    return self.td_around('buttons', button_str)

  def inline_create_cell(self):
    return self.buttons_cell([Button('Save new')])


def get_edit_button_for_column(list_url):
  return AButton('Edit', '{}/<%= id %>'.format(list_url))


def get_delete_button_for_column(delete_button_text='Delete'):
  return Button(delete_button_text, 'delete')


class DeleteColumn(ButtonsColumn):
  def __init__(
      self, delete_button_text='Delete', prepend_buttons=None):
    prepend_buttons = prepend_buttons or []
    buttons = prepend_buttons + [
        get_delete_button_for_column(delete_button_text=delete_button_text)]
    super().__init__(buttons)


class EditDeleteColumn(DeleteColumn):
  def __init__(self, model, delete_button_text='Delete', list_url=None):
    list_url = list_url or '/{}'.format(lower_case_plural(model))
    prepend_buttons = [get_edit_button_for_column(list_url)]
    super().__init__(
        delete_button_text=delete_button_text,
        prepend_buttons=prepend_buttons)
