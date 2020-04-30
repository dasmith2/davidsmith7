from datetime import date

from djaveForm.button import Button
from djaveForm.form import Form
from djaveDT import now, tz_dt_to_tz_dt
from djaveTable.problem import Problem
from djaveTable.table import Table

from tracktime.fields import work_type_field, project_field
from tracktime.models import Tracked, WorkType, Project


class StartTheClockForm(Form):
  def __init__(self):
    self.work_type_field = work_type_field(tracked=None)
    self.project_field = project_field(tracked=None)
    self.start_button = Button('Start the clock', button_type='submit')
    super().__init__([
        self.work_type_field, self.project_field, self.start_button])

  def start(self, user, nnow=None):
    nnow = nnow or now()
    Tracked.objects.create(
        user=user,
        work_type=WorkType.objects.get(pk=self.work_type_field.value),
        project=Project.objects.get(pk=self.project_field.value),
        date=nnow.date(),
        started=nnow)

  def display(self, punch_the_clock_table, display_started_column):
    row = [self.work_type_field, self.project_field]
    if display_started_column:
      row.append('')
    row.append(self.start_button)
    punch_the_clock_table.create_row(row)


class StopTheClockForm(Form):
  def __init__(self, stoppable):
    self.stoppable = stoppable
    # I include the pk here in case there's some confusion about which
    # trackable we're stopping the clock on.
    self.stop_button = Button(
        'Punch out', button_type='submit', pk=stoppable.pk)
    self.cancel_button = Button(
        'Cancel', button_type='submit', pk=stoppable.pk)
    super().__init__([self.stop_button, self.cancel_button])

  def stop(self, nnow=None):
    self.stoppable.stop(nnow=nnow)

  def cancel(self):
    self.stoppable.delete()

  def display(self, punch_the_clock_table, nnow=None):
    start_time = tz_dt_to_tz_dt(self.stoppable.started).time()
    problem = ''
    if self.form_data_was_set() and not self.is_valid():
      problem = Problem(self.explain_why_not_valid(nnow=nnow))
    punch_the_clock_table.create_row([
        self.stoppable.work_type.name, self.stoppable.project.name,
        start_time, [self.stop_button, self.cancel_button, problem]])

  def explain_why_not_valid(self, nnow=None):
    nnow = nnow or now()
    if self.stop_button.get_was_clicked() and (
        self.stoppable.started_basically_equals(nnow)):
      return 'Barely any time passed yet'

  def is_valid(self, nnow=None):
    return not self.explain_why_not_valid(nnow=nnow)


class PunchTheClockTable(Table):
  def __init__(self, user, day, form_data=None, nnow=None):
    self.user = user
    self.day = day
    self.form_data = form_data
    nnow = nnow or now()
    self.today = nnow.date().today()

    stop_form = None
    start_form = self.get_start_form(form_data, user, nnow=nnow)
    can_stop_clock = False

    abandoned = []
    for tracked in self.get_unpunched():
      if tracked.date == self.today:
        stop_form = StopTheClockForm(tracked)
        stop_clicked = False
        cancel_clicked = False
        if form_data:
          stop_form.set_form_data(form_data)
          stop_clicked = stop_form.stop_button.get_was_clicked()
          cancel_clicked = stop_form.cancel_button.get_was_clicked()
        can_stop_clock = True
        if stop_clicked or cancel_clicked:
          if stop_form.is_valid():
            can_stop_clock = False
            if stop_clicked:
              stop_form.stop()
            if cancel_clicked:
              stop_form.cancel()
      else:
        abandoned.append(tracked)

    display_started_column = abandoned or can_stop_clock
    columns = ['Work type', 'Project', '']
    if display_started_column:
      columns = ['Work type', 'Project', 'Started', '']
    super().__init__(columns)

    if can_stop_clock:
      stop_form.display(self)
    elif start_form:
      start_form.display(self, display_started_column=bool(abandoned))

    if abandoned:
      self.display_abandoned(abandoned)

  def get_start_form(self, form_data, user, nnow=None):
    start_form = None
    if self.day == self.today:
      start_form = StartTheClockForm()
      start_clicked = False
      if form_data:
        start_form.set_form_data(form_data)
        start_clicked = start_form.start_button.get_was_clicked()
      if start_clicked:
        if start_form.is_valid():
          start_form.start(user, nnow=nnow)
          start_form = StartTheClockForm()
    return start_form

  def display_abandoned(self, abandoned):
    for tracked in abandoned:
      delete = Button('Abandoned. Delete', pk=abandoned.pk)
      self.create_row([
          tracked.work_type.name, tracked.project.name, tracked.started,
          delete], pk=abandoned.pk)

  def is_visible(self):
    return bool(self.rows)

  def get_unpunched(self):
    return Tracked.objects.filter(
        user=self.user, started__isnull=False,
        stopped__isnull=True).select_related('work_type', 'project')
