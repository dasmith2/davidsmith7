from django.shortcuts import reverse
from django.template.loader import render_to_string
from djaveCRUDTable.columns import ButtonsColumn, EditFieldColumn
from djaveCRUDTable.crud_table import CRUDTable, HIDDEN_NOT_DELETED_FILTER
from djaveHTML.button import Button


class ToDoButtonsColumn(ButtonsColumn):
  def __init__(self):
    # In the case of rows that represent existing ToDos, the Done button is
    # added via Javascript by setup_set_clear_dt_green_mode. The Delete button
    # is wired up by to_dos.js
    super().__init__([])

  def inline_create_cell(self):
    to_do = Button('To do', **{'data-done': 'null'})
    self.add_button_attrs(to_do)
    did = Button('Did', **{'data-done': 'now'})
    self.add_button_attrs(did)
    return self.buttons_cell([to_do, did])

  def add_button_attrs(self, button):
    pass


class ToDos(CRUDTable):
  def __init__(self, *additional_columns):
    # In this case, there's a "Punch out" button next to the title. The
    # template handles it.
    list_header = None
    super().__init__(
        self.model(), self.columns(), visible_filters=self.filters(),
        save_new_defaults={'creator': 'me'},
        list_url=self.list_url(), list_header=list_header,
        hidden_filters=self.hidden_filters(),
        show_column_headers=False, inline_create=True,
        modified_row_callback='new_to_do_row',
        confirm_delete_question='Delete to do?',
        inline_create_callback='inline_create_to_do_callback',
        nav_css_class='to_dos_nav')
    self.add_js(render_to_string('js/to_dos.js'))

  def filters(self):
    return None

  def columns(self):
    return [EditFieldColumn(self.model(), 'description')]

  def list_url(self):
    return reverse('to_dos')

  def hidden_filters(self):
    return [HIDDEN_NOT_DELETED_FILTER]

  def model(self):
    raise NotImplementedError(
        'model is not implemented because ToDos is a base class.')
