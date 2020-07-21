from collections import namedtuple

from django.shortcuts import reverse
from djaveClassMagic.edit_list_table import EditListTable
from djaveDT import now, tz_dt_to_tz_dt
from djaveForm.button import Button
from djaveForm.form import Form
from djaveTable.problem import Problem
from djaveTable.cell_content import InHref

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.models.project import Project
from tracktime.models.latest_project import set_latest_project


class StartProjectForm(Form):
  StartProjectInfo = namedtuple(
      'StartProjectInfo', 'project button can_click_start')

  def __init__(
      self, user, see_all_tasks_button=False, only_show_has_to_do_list=False):
    self.start_project_infos = []
    form_buttons = []
    self.has_projects = False
    for project in Project.live.allowed_by_user(user).order_by('name'):
      if project.has_to_do_list or not only_show_has_to_do_list:
        self.has_projects = True
        button = None
        if project.use_clock:
          button = Button(
              'Start the clock', pk=project.pk, button_type='submit')
          form_buttons.append(button)
        else:
          url = reverse('to_do', kwargs={'project_pk': project.pk})
          button = InHref(project.name, url, button=True)
        self.start_project_infos.append(
            self.StartProjectInfo(project, button, bool(button)))
    if see_all_tasks_button:
      button = InHref(
          'See ALL tasks', reverse('all_tasks'), classes=['all_tasks'],
          button=True)
      self.start_project_infos.append(
          self.StartProjectInfo(None, button, False))
    super().__init__(form_buttons)

  def started_clock_on_project(self, user, nnow=None):
    for start_project_info in self.start_project_infos:
      if start_project_info.can_click_start and (
          start_project_info.button.get_was_clicked()):
        started_project = start_project_info.project
        self.start(user, started_project, nnow=nnow)
        set_latest_project(user, started_project)
        return started_project

  def start(self, user, project, nnow=None):
    nnow = nnow or now()
    ProjectWorkSession.live.create(
        user=user, project=project, date=nnow.date(), started=nnow)

  def display(self, punch_the_clock_table, display_started_column):
    for start_project_info in self.start_project_infos:
      cells = []
      if start_project_info.project and start_project_info.project.use_clock:
        cells.append(start_project_info.project.name)
      else:
        cells.append('')
      if display_started_column:
        cells.append('')
      cells.append(start_project_info.button)
      punch_the_clock_table.create_row(cells)


class StopTheClockForm(Form):
  def __init__(self, stoppable: ProjectWorkSession):
    self.stoppable = stoppable
    self.stop_button = Button('Punch out', button_type='submit')
    self.cancel_button = Button('Cancel', button_type='submit')
    super().__init__([self.stop_button, self.cancel_button])

  def stop(self, nnow=None):
    self.stoppable.stop(nnow=nnow)

  def cancel(self, nnow=None):
    self.stoppable.mark_deleted(nnow=nnow)

  def display(self, punch_the_clock_table, nnow=None):
    start_time = tz_dt_to_tz_dt(self.stoppable.started).time()
    problem = ''
    if self.form_data_was_set() and not self.is_valid(nnow=nnow):
      problem = Problem(self.explain_why_not_valid(nnow=nnow))
    punch_the_clock_table.create_row([
        self.stoppable.project.name, start_time,
        [self.stop_button, self.cancel_button, problem]])

  def explain_why_not_valid(self, nnow=None):
    return self.stoppable.explain_why_can_not_stop(nnow=nnow)

  def is_valid(self, nnow=None):
    return not self.explain_why_not_valid(nnow=nnow)


class PunchTheClockTable(EditListTable):
  def __init__(
      self, user, day, show_abandoned=True, form_data=None, nnow=None,
      see_all_tasks_button=False, only_show_has_to_do_list=False):
    self.user = user
    self.day = day
    self.show_abandoned = show_abandoned
    self.form_data = form_data
    nnow = nnow or now()
    self.today = nnow.date()

    stop_form = None

    start_form = StartProjectForm(
        user, see_all_tasks_button=see_all_tasks_button,
        only_show_has_to_do_list=only_show_has_to_do_list)
    self.has_projects = start_form.has_projects
    self.started_clock_on_project = None
    if start_form.a_button_was_clicked(form_data):
      start_form.set_form_data(form_data)
      self.started_clock_on_project = start_form.started_clock_on_project(
          user, nnow=nnow)

    a_clock_can_be_stopped = False
    abandoned = []
    for work_session in ProjectWorkSession.live.get_clock_never_stopped(
        user, nnow=nnow):
      if work_session.clock_running(nnow=nnow):
        stop_form = StopTheClockForm(work_session)
        stop_clicked = False
        cancel_clicked = False
        if stop_form.a_button_was_clicked(form_data):
          stop_form.set_form_data(form_data)
          stop_clicked = stop_form.stop_button.get_was_clicked()
          cancel_clicked = stop_form.cancel_button.get_was_clicked()
        a_clock_can_be_stopped = True
        if stop_clicked or cancel_clicked:
          if stop_form.is_valid(nnow=nnow):
            a_clock_can_be_stopped = False
            if stop_clicked:
              stop_form.stop(nnow=nnow)
            if cancel_clicked:
              stop_form.cancel(nnow=nnow)
      else:
        abandoned.append(work_session)

    display_started_column = a_clock_can_be_stopped or (
        abandoned and self.show_abandoned)
    columns = []
    if display_started_column:
      columns = ['Project', 'Started', '']
    super().__init__(ProjectWorkSession, columns, classes=['margin-top'])
    self.wire_up_delete_ajax('.abandoned')

    if a_clock_can_be_stopped:
      stop_form.display(self)
    elif self.day == self.today:
      start_form.display(self, display_started_column=display_started_column)

    if abandoned and self.show_abandoned:
      self.display_abandoned(abandoned)

  def display_abandoned(self, abandoned):
    for work_session in abandoned:
      delete = Button('Abandoned session. Delete.', key_prefix='abandoned')
      self.create_row([
          work_session.project.name, work_session.started, delete],
          pk=work_session.pk)

  def is_visible(self):
    return bool(self.rows)
