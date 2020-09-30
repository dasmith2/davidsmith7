from collections import namedtuple

from djaveDT import tz_dt_to_tz_dt, now
from djaveHTML.button import Button
from djaveHTML.form import Form
from djaveHTML.problem import Problem
from djaveHTML.table import Table
from djaveHTML.simple_form_as_html import simple_form_as_html

from tracktime.models.project_work_session import (
    ProjectWorkSession, start_clock_on_project)
from tracktime.models.project import Project


class PunchTheClock(object):
  def __init__(self, user, day, form_data, nnow=None):
    self.has_projects = True
    self.started_project = None

    self.user = user
    self.day = day
    self.form_data = form_data

    self.content = None

    if not self.use_stop_the_clock_form(nnow=nnow):
      projects = Project.live.allowed_by_user(self.user).filter(
          use_clock=True).order_by('name')
      self.has_projects = bool(projects)
      if self.has_projects:
        start_the_clock_form = StartTheClockForm(projects)
        self.content = start_the_clock_form
        self.started_project = start_the_clock_form.started_clock_on_project(
            form_data, self.user, nnow=nnow)
        if self.started_project:
          self.use_stop_the_clock_form(nnow=nnow)

  def use_stop_the_clock_form(self, nnow=None):
    for work_session in ProjectWorkSession.live.get_clock_never_stopped(
        self.user, nnow=nnow):
      if work_session.abandoned(nnow=nnow):
        work_session.mark_deleted()
      else:
        stop_form = StopTheClockForm(work_session, nnow=nnow)
        stop_clicked = False
        cancel_clicked = False
        if stop_form.a_button_was_clicked(self.form_data):
          stop_form.set_form_data(self.form_data)
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
        if a_clock_can_be_stopped:
          self.content = stop_form
          return self.content

  def as_html(self):
    return self.content.as_html()


class StartTheClockForm(Form):
  StartProjectInfo = namedtuple('StartProjectInfo', 'project button')

  def __init__(self, projects):
    self.start_project_infos = []
    form_buttons = []
    for project in projects:
      button = Button(
          project.name, key_prefix='startclock', pk=project.pk,
          button_type='submit')
      form_buttons.append(button)
      self.start_project_infos.append(self.StartProjectInfo(project, button))
    super().__init__(form_buttons)

  def started_clock_on_project(self, form_data, user, nnow=None):
    if not form_data:
      return
    for start_project_info in self.start_project_infos:
      if start_project_info.button.get_was_clicked(form_data):
        started_project = start_project_info.project
        start_clock_on_project(user, started_project, nnow=nnow)
        return started_project

  def as_html(self):
    return simple_form_as_html(self)


class StopTheClockForm(Form):
  def __init__(self, stoppable: ProjectWorkSession, nnow=None):
    self.stoppable = stoppable
    self.nnow = nnow or now()
    self.stop_button = Button('Punch out', button_type='submit')
    self.cancel_button = Button('Cancel', button_type='submit')
    super().__init__([self.stop_button, self.cancel_button])

  def stop(self, nnow=None):
    self.stoppable.stop(nnow=nnow)

  def cancel(self, nnow=None):
    self.stoppable.mark_deleted(nnow=nnow)

  def get_table(self):
    table = Table(
        ['Project', 'Started', ''], css_classes=['margin-top-half'])

    start_time = tz_dt_to_tz_dt(self.stoppable.started).time()
    problem = ''
    if self.form_data_was_set() and not self.is_valid(nnow=self.nnow):
      problem = Problem(self.explain_why_not_valid(nnow=self.nnow))
    table.create_row([
        self.stoppable.project.name, start_time,
        [self.stop_button, self.cancel_button, problem]])
    return table

  def as_html(self, nnow=None):
    return self.get_table().as_html()

  def explain_why_not_valid(self, nnow=None):
    return self.stoppable.explain_why_can_not_stop(nnow=nnow)

  def is_valid(self, nnow=None):
    return not self.explain_why_not_valid(nnow=nnow)
