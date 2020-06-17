from djaveClass.edit_list_table import EditListTable
from djaveDT import now
from djaveForm.button import Button
from djaveForm.form import Form
from djaveForm.field import TextAreaField
from djaveTable.table import Cell

from tracktime.models.to_do import ToDo


class ToDoForm(Form):
  def __init__(self):
    super().__init__(self.create_fields())

  def create_fields(self):
    self.description_field = TextAreaField('new_description', required=True)
    self.to_do_button = Button('To do', button_type='submit')
    self.did_button = Button('Did', button_type='submit')
    return [self.description_field, self.to_do_button, self.did_button]

  def get_description(self):
    return self.description_field.get_value()


class ToDoTable(EditListTable):
  def __init__(self, user, form_data, nnow=None):
    super().__init__(ToDo)
    self.user = user
    self.form_data = form_data

    self.setup_enter_new(nnow=nnow)
    self.setup_existing()

    self.wire_up_edit_ajax('description')

  def setup_enter_new(self, nnow=None):
    nnow = nnow or now()
    self.form = self.get_form()
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.form.is_valid():
        to_do = self.create_to_do()
        if self.form.did_button.get_was_clicked():
          to_do.done = nnow
          to_do.done_by = self.user
          to_do.save()
        self.form = self.get_form()

    self.create_row(self.cells_for_enter_new())

  def setup_existing(self):
    for to_do in self.get_not_long_done():
      classes = None
      if to_do.done:
        classes = ['to_done']  # So as not to conflict with the done button
      self.create_row(
          self.cells_for_existing(to_do), pk=to_do.pk, classes=classes)

  # From here on out it's stuff you probably want to override in your
  # FooToDoTable. See ProjectToDoTable for an example.
  def get_form(self):
    return ToDoForm()

  def create_to_do(self):
    return ToDo.live.create(
        creator=self.user, description=self.form.get_description())

  def cells_for_enter_new(self):
    return [self.form.description_field, [
        self.form.to_do_button, self.form.did_button]]

  def get_not_long_done(self):
    return ToDo.live.not_long_done(self.user)

  def cells_for_existing(self, to_do):
    description = TextAreaField(
        'description', default=to_do.description, required=False)
    return [description, Cell(None, ['buttons'])]
