from datetime import date, timedelta

from djaveTable.table import Table, Cell
from djaveForm.button import Button
from djaveForm.field import DateField, Field
from djaveForm.form import Form
from tracktime.fields import work_type_field, project_field


class FiltersForm(Form):
  def __init__(self):
    super().__init__()
    default_starting_on = date.today() - timedelta(days=7)
    self.starting_on = self.new_form_element(DateField(
        key_prefix='starting_on', default=default_starting_on))
    self.ending_on = self.new_form_element(DateField(
        key_prefix='ending_on'))
    self.work_type = self.new_form_element(work_type_field())
    self.project = self.new_form_element(project_field())

    for element in self.form_elements:
      if isinstance(element, Field):
        element.required = False


class AddUpTimeFiltersTable(Table):
  def __init__(self):
    super().__init__()
    self.form = FiltersForm()

    for title, element in [
        ('Starting on', self.form.starting_on),
        ('Ending on', self.form.ending_on),
        ('Project', self.form.project),
        ('Work type', self.form.work_type),
        ('', Button('Filter', button_type='submit'))]:
      self.create_row([
          Cell(title, is_header=True), element])

  def set_form_data(self, form_data):
    self.form.set_form_data(form_data)
