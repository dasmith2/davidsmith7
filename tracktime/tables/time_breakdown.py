from collections import namedtuple
from datetime import timedelta

from django.shortcuts import reverse
from django.template import loader
from djaveDT import now
from djaveReport.date_range_report import DateRangeReport

from tracktime.models.project import Project
from tracktime.models.to_do import ToDo
from tracktime.models.project_work_session import ProjectWorkSession


def time_breakdown_url(project):
  return '{}?project={}'.format(reverse('time_breakdown'), project.pk)


class TimeBreakdown(DateRangeReport):
  def __init__(self, request_get, user, nnow=None):
    nnow = nnow or now()
    default_from_date = nnow.date() - timedelta(days=7)
    default_to_date = nnow.date()
    super().__init__(default_from_date, default_to_date, request_get)

    project = None
    if 'project' in request_get:
      project = Project.live.filter(pk=request_get['project']).first()

    self.time_breakdown_content = TimeBreakdownContent(
        user, project, self.from_date(), self.to_date())
    self.add_content(self.time_breakdown_content)


class TimeBreakdownContent(object):
  def __init__(self, user, project, from_date, to_date, tz_str=None):
    self.user = user
    self.project = project
    self.tz_str = tz_str
    self.work_session_descriptions = self.get_work_sessions(
        user, project, from_date, to_date, tz_str=tz_str)

  def get_work_sessions(self, user, project, from_date, to_date, tz_str=None):
    work_session_descriptions = []

    work_session_i = 0
    work_sessions = self._get_work_sessions(user, project, from_date, to_date)

    to_do_i = 0
    to_dos = self._get_to_dos(user, project, from_date, to_date)
    self.total = 0.0

    if not work_sessions and not to_dos:
      return

    show_project = not project
    on_work_session = None
    while work_session_i < len(work_sessions) or to_do_i < len(to_dos):
      if work_session_i >= len(work_sessions) or (
          to_do_i < len(to_dos) and (
              work_sessions[work_session_i].get_started(tz_str=tz_str) > (
                  to_dos[to_do_i].done))):
        if not on_work_session:
          on_work_session = WorkSessionDescription(
              '(marked done outside a work session)', [])
          work_session_descriptions.append(on_work_session)
        to_do = to_dos[to_do_i]
        to_do_i += 1
        if to_do.project == project or not project:
          on_work_session.to_do_descriptions.append(
              self._to_do_description(to_do, show_project))
      else:
        work_session = work_sessions[work_session_i]
        work_session_i += 1
        if work_session.project == project or not project:
          on_work_session = WorkSessionDescription(
              self._time_description(work_session, show_project), [])
          work_session_descriptions.append(on_work_session)
          if work_session.hours:
            self.total += work_session.hours

    # I want work sessions in reverse chronological order so when the user
    # punches out and comes to this report page, the most recent stuff they
    # worked on is up top.
    work_session_descriptions.reverse()
    return work_session_descriptions

  def _get_work_sessions(self, user, project, from_date, to_date):
    work_sessions = list(ProjectWorkSession.live.done_by_user_and_date_range(
        user, from_date, to_date))
    work_sessions.sort(key=lambda x: x.get_started())
    if project:
      work_sessions = list(filter(
          lambda x: x.project == project, work_sessions))
    return work_sessions

  def _get_to_dos(self, user, project, from_date, to_date):
    to_dos = list(ToDo.live.done_by_user_in_date_range(
        user, from_date, to_date).order_by('done'))
    if project:
      to_dos = list(filter(lambda x: x.project == project, to_dos))
    return to_dos

  def _time_description(self, work_session, show_project):
    description = work_session.describe_time_span(self.tz_str)
    if show_project:
      description = '{} {}'.format(work_session.project.name, description)
    return description

  def _to_do_description(self, to_do, show_project):
    description = to_do.description
    if show_project:
      description = '{} {}'.format(to_do.project.name, description)
    return description

  def as_html(self):
    template = loader.get_template('time_breakdown.html')
    context = {
        'work_session_descriptions': self.work_session_descriptions,
        'project': self.project,
        'total': round(self.total, 2)}
    return template.render(context)


WorkSessionDescription = namedtuple(
    'WorkSessionDescription', 'time_description to_do_descriptions')
