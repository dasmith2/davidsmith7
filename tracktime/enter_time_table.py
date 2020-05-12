from djaveDT import dt_to_time_str
from djaveTable.table import Table, Cell
from djaveForm.form import Form
from djaveForm.button import Button

from tracktime.fields import project_field, hours_field
from tracktime.models.tracked import Tracked
from tracktime.models.project import Project
from tracktime.models.latest_project import set_latest_project


class EnterTimeForm(Form):
  def __init__(self, user):
    self.project_field = project_field(user, tracked=None)
    self.hours_field = hours_field(tracked=None)
    self.save_button = Button('Save new', button_type='submit')
    super().__init__([
        self.project_field, self.hours_field,
        self.save_button])


class EnterTimeTable(Table):
  def __init__(self, user, day, form_data=None):
    self.day = day
    self.user = user
    self.form_data = form_data

    tracked = self.get_tracked()
    hours = self.total_hours(tracked)
    super().__init__(['Project', 'Hours: {}'.format(hours), ''])

    self.setup_enter_new()

    self.setup_edit_existing(tracked)

  def setup_enter_new(self):
    self.form = EnterTimeForm(self.user)
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
    row = [
        self.form.project_field, self.form.hours_field, self.form.save_button]
    self.create_row(row, classes=['new'])

  def total_hours(self, got_tracked):
    total = 0.0
    for tracked in got_tracked:
      if tracked.hours:
        total += tracked.hours
    return total

  def get_tracked(self):
    """ If the hours aren't set, it isn't tracked yet really """
    return Tracked.objects.filter(
        user=self.user, date=self.day, hours__gt=0).select_related(
            'project').order_by('pk')

  def setup_edit_existing(self, got_tracked):
    for tracked in got_tracked:
      delete = Button('Delete', pk=tracked.pk)
      hours = str(tracked.hours)
      if tracked.started:
        hours = '{} starting at {}'.format(
            hours, dt_to_time_str(tracked.started))
      self.create_row([
          tracked.project.name, Cell(hours, classes=['hours']), delete],
          pk=tracked.pk)

  def is_valid(self):
    return self.form.is_valid()

  def save(self):
    project = Project.objects.get(pk=self.form.project_field.value)
    hours = self.form.hours_field.value
    set_latest_project(self.user, project)
    return Tracked.objects.create(
        user=self.user, project=project, date=self.day,
        hours=hours)
