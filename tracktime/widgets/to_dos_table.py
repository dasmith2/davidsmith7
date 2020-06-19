from djaveClassMagic.edit_list_table import EditListTable
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


class ToDosTable(EditListTable):
  def __init__(self, user, form_data, nnow=None):
    super().__init__(ToDo)

    self.created_from_date = None
    self.created_to_date = None
    self.status = None

    self.user = user
    self.form_data = form_data
    self.nnow = nnow

    self._rows_populated = False

    self.wire_up_edit_ajax('description')

  def should_filter_created(self):
    how_many_specified = int(bool(self.created_from_date)) + int(
        bool(self.created_to_date))
    if how_many_specified in (0, 2):
      return bool(self.created_from_date)
    raise Exception(
        'Specify precisely both or neither of created_from_date and '
        'created_to_date')

  def as_html(self):
    if not self._rows_populated:
      raise Exception(
          'You have to call populate_rows after __init__ but before rendering')
    return super().as_html()

  def populate_rows(self):
    # populate_rows can't happen on __init__ because I want to give the all
    # project to dos page a chance to parse the query string arguments and
    # decide whether or not to display a project column.
    if self._rows_populated:
      return
    self._rows_populated = True

    self.setup_enter_new(nnow=self.nnow)
    self.setup_existing()
    self.headers = self.get_headers()

  def get_headers(self):
    if self.should_filter_created():
      return []
    return None

  def setup_enter_new(self, nnow=None):
    nnow = nnow or now()
    self.form = self.get_form()
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.form.is_valid():
        to_do = self.create_to_do()
        if self.form.did_button.get_was_clicked():
          to_do.done = nnow
          to_do.save()
        self.form = self.get_form()

    self.create_row(self.cells_for_enter_new())

  def setup_existing(self):
    for to_do in self.get_to_dos():
      classes = None
      if to_do.done:
        classes = ['to_done']  # So as not to conflict with the done button
      self.create_row(
          self.cells_for_existing(to_do), pk=to_do.pk, classes=classes)

  # From here on out it's stuff you probably want to override in your
  # FooToDosTable. See ProjectToDosTable for an example.
  def get_form(self):
    return ToDoForm()

  def create_to_do(self):
    return ToDo.live.create(
        creator=self.user, description=self.form.get_description())

  def cells_for_enter_new(self):
    cells = [self.form.description_field]
    if self.should_filter_created():
      cells.append('')
    cells.append([self.form.to_do_button, self.form.did_button])
    return cells

  def get_to_dos(self):
    manager = self.to_do_class().live
    to_dos = manager.allowed_by_user(self.user)
    if self.should_filter_created():
      to_dos = manager.filter_created(
          to_dos, self.created_from_date, self.created_to_date)
    else:
      to_dos = manager.filter_not_long_done(to_dos)

    if self.status:
      to_dos = manager.filter_status(to_dos, self.status)

    if self.should_filter_created():
      return manager.order_for_all(to_dos)
    return manager.order_for_doing(to_dos)

  def to_do_class(self):
    return ToDo

  def cells_for_existing(self, to_do):
    description = TextAreaField(
        'description', default=to_do.description, required=False)
    cells = [description]
    if self.should_filter_created():
      cells.append(to_do.created.date())
    cells.append(Cell(None, ['buttons']))
    return cells
