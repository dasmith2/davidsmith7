from djaveDT import dt_to_time_str
from djaveTable.table import Table, Cell
from djaveForm.form import Form
from djaveForm.button import Button

from tracktime.fields import work_type_field, project_field, hours_field
from tracktime.models import Tracked, WorkType, Project


class EnterTimeForm(Form):
  def __init__(self):
    self.work_type_field = work_type_field(tracked=None)
    self.project_field = project_field(tracked=None)
    self.hours_field = hours_field(tracked=None)
    self.save_button = Button('Save', button_type='submit')
    super().__init__([
        self.work_type_field, self.project_field, self.hours_field,
        self.save_button])


class EnterTimeTable(Table):
  def __init__(self, user, day, form_data=None):
    super().__init__(['Work type', 'Project', 'Hours', ''])
    self.day = day
    self.user = user
    self.form_data = form_data
    self.setup_enter_new()
    self.setup_edit_existing()

  def setup_enter_new(self):
    self.form = EnterTimeForm()
    if self.form_data:
      self.form.set_form_data(self.form_data)
    row = [
        self.form.work_type_field, self.form.project_field,
        self.form.hours_field, self.form.save_button]
    self.create_row(row, classes=['new'])

  def get_tracked(self):
    """ If the hours aren't set, it isn't tracked yet really """
    return Tracked.objects.filter(
        user=self.user, date=self.day, hours__gt=0).select_related(
            'work_type', 'project').order_by('pk')

  def setup_edit_existing(self):
    for tracked in self.get_tracked():
      delete = Button('Delete', pk=tracked.pk)
      hours = str(tracked.hours)
      if tracked.started:
        hours = '{} starting at {}'.format(
            hours, dt_to_time_str(tracked.started))
      self.create_row([
          tracked.work_type.name, tracked.project.name,
          Cell(hours, classes=['hours']), delete], pk=tracked.pk)

  def is_valid(self):
    return self.form.is_valid()

  def save(self):
    work_type = WorkType.objects.get(pk=self.form.work_type_field.value)
    project = Project.objects.get(pk=self.form.project_field.value)
    hours = self.form.hours_field.value
    return Tracked.objects.create(
        user=self.user, work_type=work_type, project=project, date=self.day,
        hours=hours)
