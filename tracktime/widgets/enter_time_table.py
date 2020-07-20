from djaveClassMagic.edit_list_table import EditListTable
from djaveDT import dt_to_time_str
from djaveTable.table import Cell
from djaveForm.form import Form
from djaveForm.button import Button

from tracktime.fields import project_field, hours_field
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.models.project import Project
from tracktime.models.latest_project import set_latest_project


class EnterTimeForm(Form):
  def __init__(self, user):
    self.project_field = project_field(user, use_clock=True)
    self.hours_field = hours_field()
    self.save_button = Button('Save new', button_type='submit')
    super().__init__([
        self.project_field, self.hours_field,
        self.save_button])


class EnterTimeTable(EditListTable):
  """ Saving a new one is done by posting a form. Deleting an existing one is
  done by AJAX. In general, I think that when a page is talking about a single
  instance of something it should be manipulated through posting the page,
  but when you have a list of things, those should be done through AJAX. """
  def __init__(self, user, day, form_data, nnow=None):
    self.day = day
    self.user = user
    self.form_data = form_data
    super().__init__(ProjectWorkSession, classes=['margin-top-half'])

    # This might save a new one if the form is valid so it has to go before we
    # load this user's WorkSessions.
    self.setup_enter_new()

    work_session = ProjectWorkSession.live.done_by_user_and_date(
        self.user, self.day, nnow=nnow)
    self.setup_edit_existing(work_session)

    hours = self.total_hours(work_session)
    self.headers = ['Project', 'Hours: {}'.format(hours), '']
    self.wire_up_delete_ajax(
        '.delete', confirm_question='Delete work session?')

  def setup_enter_new(self):
    self.form = EnterTimeForm(self.user)
    if self.form.a_button_was_clicked(self.form_data):
      self.form.set_form_data(self.form_data)
      if self.is_valid():
        self.save()
        self.form = EnterTimeForm(self.user)
    hours_cell = Cell(
        self.form.hours_field, additional_attrs={'style': 'text-align: right'})
    row = [self.form.project_field, hours_cell, self.form.save_button]
    self.create_row(row, classes=['new'])

  def total_hours(self, got_work_session):
    total = 0.0
    for work_session in got_work_session:
      if work_session.hours:
        total += work_session.hours
    return round(total, 2)

  def setup_edit_existing(self, got_work_session):
    for work_session in got_work_session:
      delete = Button('Delete')
      hours = work_session.hours
      if work_session.started:
        hours = '{} starting at {}'.format(
            hours, dt_to_time_str(work_session.started))
      self.create_row([
          work_session.project.name,
          Cell(hours, classes=['hours', 'width-135']),
          delete], pk=work_session.pk)

  def is_valid(self):
    return self.form.is_valid()

  def save(self):
    project = Project.live.get(pk=self.form.project_field.get_value())
    hours = self.form.hours_field.get_value()
    set_latest_project(self.user, project)
    return ProjectWorkSession.live.create(
        user=self.user, project=project, date=self.day,
        hours=hours)
