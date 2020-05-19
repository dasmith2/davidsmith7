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
  """ Saving a new one is done by posting a form. Deleting an existing one is
  done by AJAX. In general, I think that when a page is talking about a single
  instance of something it should be manipulated through posting the page,
  but when you have a list of things, those should be done through AJAX. """
  def __init__(self, user, day, form_data, nnow=None):
    self.day = day
    self.user = user
    self.form_data = form_data
    super().__init__()

    # This might save a new one if the form is valid so it has to go before we
    # load this user's Trackeds.
    self.setup_enter_new()

    tracked = Tracked.live.done_by_user_and_date(
        self.user, self.day, nnow=nnow)
    self.setup_edit_existing(tracked)

    hours = self.total_hours(tracked)
    self.headers = ['Project', 'Hours: {}'.format(hours), '']

  def setup_enter_new(self):
    self.form = EnterTimeForm(self.user)
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.is_valid():
        self.save()
        self.form = EnterTimeForm(self.user)
    row = [
        self.form.project_field, self.form.hours_field, self.form.save_button]
    self.create_row(row, classes=['new'])

  def total_hours(self, got_tracked):
    total = 0.0
    for tracked in got_tracked:
      if tracked.hours:
        total += tracked.hours
    return round(total, 2)

  def setup_edit_existing(self, got_tracked):
    for tracked in got_tracked:
      delete = Button('Delete')
      hours = tracked.hours
      if tracked.started:
        hours = '{} starting at {}'.format(
            hours, dt_to_time_str(tracked.started))
      self.create_row([
          tracked.project.name, Cell(hours, classes=['hours']), delete],
          pk=tracked.pk)

  def is_valid(self):
    return self.form.is_valid()

  def save(self):
    project = Project.live.get(pk=self.form.project_field.value)
    hours = self.form.hours_field.value
    set_latest_project(self.user, project)
    return Tracked.live.create(
        user=self.user, project=project, date=self.day,
        hours=hours)
