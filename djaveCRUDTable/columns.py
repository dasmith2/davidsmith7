from django.utils.safestring import mark_safe
from djaveClassMagic.cases import lower_case_plural
from djaveHTML.a import AButton
from djaveHTML.button import Button


class DisplayColumn(object):
  """ This is an abstract base class. You probably want to use
  DisplayFieldColumn or ButtonsColumn or make your own type of column. """
  def __init__(self, header, cell_template, header_css_class=None):
    self.header = header
    self.cell_template = cell_template
    self.header_css_class = header_css_class


class DisplayFieldColumn(DisplayColumn):
  def __init__(self, header, field_name, header_css_class=None):
    cell_template = mark_safe('<td class="{}"><%= {} %></td>'.format(
        field_name, field_name))
    super().__init__(header, cell_template, header_css_class)


class ButtonsColumn(DisplayColumn):
  def __init__(self, buttons):
    self.buttons = buttons
    if buttons:
      self.buttons[-1].add_class('last-button')
    super().__init__(mark_safe('&nbsp;'), self.cell_template())

  def cell_template(self):
    """ DO NOT SUBMIT <td class="buttons">
      <a href="/{}/<%= id %>" class="button edit">Edit</a>
      <button class="delete last-button">{}</a>
    </td>"""
    button_str = ''.join([button.as_html() for button in self.buttons])
    return mark_safe('<td class="buttons">{}</td>'.format(button_str))


class EditDeleteColumn(ButtonsColumn):
  def __init__(self, model, delete_button_text='Delete'):
    edit_url = '/{}/<%= id %>'.format(lower_case_plural(model))
    edit = AButton('Edit', edit_url)
    delete = Button(delete_button_text, 'delete')
    super().__init__([edit, delete])
