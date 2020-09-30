from djaveCRUDTable.edit_table import EditTable
from djaveHTML.button import Button
from djaveHTML.feedback import Feedback


class EditModelTable(EditTable):
  def __init__(self, model, edit_field_names_or_rows, list_url):
    self.edit_field_names_or_rows = edit_field_names_or_rows
    super().__init__(model, None, list_url)

  def add_rows(self):
    self.add_field_rows(*self.edit_field_names_or_rows)
    self.add_final_row()

  def add_final_row(self):
    buttons = [
        Button('Save'), self.cancel_button, Button('Delete'), Feedback()]
    self.buttons_cell.elements.extend(buttons)
    self.create_row([self.buttons_cell])
