from collections import namedtuple

from djaveForm.button import Button
from djaveForm.form import Form
from djaveDT import now, tz_dt_to_tz_dt
from djaveTable.problem import Problem
from djaveTable.table import Table

from tracktime.models import Tracked, Project


class StartTheClockForm(Form):
  StartTheClockButton = namedtuple('StartTheClockButton', 'button project')

  def __init__(self):
    self.start_the_clock_buttons = []
    form_buttons = []
    for project in Project.objects.order_by('name'):
      form_button = Button(
          'Start the clock', pk=project.pk, button_type='submit')
      form_buttons.append(form_button)
      start_the_clock_button = self.StartTheClockButton(form_button, project)
      self.start_the_clock_buttons.append(start_the_clock_button)
    super().__init__(form_buttons)

  def started_clock_on_project(self, user, nnow=None):
    for start_the_clock_button in self.start_the_clock_buttons:
      if start_the_clock_button.button.get_was_clicked():
        started_project = start_the_clock_button.project
        self.start(user, started_project, nnow=nnow)
        return started_project

  def start(self, user, project, nnow=None):
    nnow = nnow or now()
    Tracked.objects.create(
        user=user, project=project, date=nnow.date(), started=nnow)

  def display(self, punch_the_clock_table, display_started_column):
    for start_the_clock_button in self.start_the_clock_buttons:
      row = [start_the_clock_button.project.name]
      if display_started_column:
        row.append('')
      row.append(start_the_clock_button.button)
      punch_the_clock_table.create_row(row)


class StopTheClockForm(Form):
  def __init__(self, stoppable: Tracked):
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
        self.stoppable.project.name, start_time,
        [self.stop_button, self.cancel_button, problem]])

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

    start_form = StartTheClockForm()
    self.started_clock_on_project = None
    if form_data:
      start_form.set_form_data(form_data)
      self.started_clock_on_project = start_form.started_clock_on_project(
          user, nnow=nnow)

    can_stop_clock = False

    abandoned = []
    for tracked in Tracked.objects.get_unpunched(user):
      if tracked.can_punch_out(nnow=nnow):
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
    columns = ['Project', '']
    if display_started_column:
      columns = ['Project', 'Started', '']
    super().__init__(columns)

    if can_stop_clock:
      stop_form.display(self)
    elif self.day == self.today:
      start_form.display(self, display_started_column=bool(abandoned))

    if abandoned:
      self.display_abandoned(abandoned)

  def display_abandoned(self, abandoned):
    for tracked in abandoned:
      delete = Button('Abandoned. Delete.', pk=tracked.pk, css_class='delete')
      self.create_row([
          tracked.project.name, tracked.started,
          delete], pk=tracked.pk)

  def is_visible(self):
    return bool(self.rows)
