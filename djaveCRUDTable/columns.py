from django.utils.safestring import mark_safe
from djaveClassMagic.cases import lower_case_plural
from djaveClassMagic.default_widget import default_widget
from djaveClassMagic.model_fields import model_fields
from djaveHTML.a import AButton
from djaveHTML.button import Button


class DisplayColumn(object):
  """ This is an abstract base class. You probably want to use
  DisplayFieldColumn or ButtonsColumn or make your own type of column. """
  def __init__(self, header, cell_template, header_css_class=None):
    self.header = header
    self.cell_template = cell_template
    self.header_css_class = header_css_class

  def inline_create_cell(self):
    return self.cell_template

  def safe_inline_create_cell(self):
    return mark_safe(self.inline_create_cell())

  def td_around(self, td_css_class, content):
    return mark_safe('<td class="{}">{}</td>'.format(td_css_class, content))


class EditFieldColumn(DisplayColumn):
  def __init__(self, model, field_name):
    field = model_fields(model, specific_field=field_name)
    widget = default_widget(field)
    super().__init__(
        field.display_name, self.td_around(field_name, widget.as_html()))


class DisplayFieldColumn(DisplayColumn):
  def __init__(
      self, header, field_name, header_css_class=None, cell_css_class=None):
    _cell_css_class = field_name
    if cell_css_class:
      _cell_css_class += ' {}'.format(cell_css_class)
    cell_template = self.td_around(
        _cell_css_class, '<%= {} %>'.format(field_name))
    super().__init__(header, cell_template, header_css_class)


class ButtonsColumn(DisplayColumn):
  def __init__(self, buttons):
    self.buttons = buttons
    if buttons:
      self.buttons[-1].add_class('last-button')
    super().__init__(mark_safe('&nbsp;'), self.cell_template())

  def cell_template(self):
    return self.buttons_cell(self.buttons)

  def buttons_cell(self, buttons):
    button_str = ''.join([button.as_html() for button in buttons])
    return self.td_around('buttons', button_str)


class EditDeleteColumn(ButtonsColumn):
  def __init__(self, model, delete_button_text='Delete'):
    edit_url = '/{}/<%= id %>'.format(lower_case_plural(model))
    edit = AButton('Edit', edit_url)
    delete = Button(delete_button_text, 'delete')
    super().__init__([edit, delete])
