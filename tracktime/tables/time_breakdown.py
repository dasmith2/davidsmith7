from collections import namedtuple
from datetime import timedelta

from django.template import loader
from djaveDT import now
from djaveReport.date_range_report import DateRangeReport

from tracktime.models.project import Project
from tracktime.models.to_do import ToDo
from tracktime.models.tracked import Tracked


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

    # Get work sessions
    self.work_sessions = []

    tracked_i = 0
    trackeds = list(Tracked.live.done_by_user_and_date_range(
        user, from_date, to_date))
    trackeds.sort(key=lambda x: x.get_started(tz_str=tz_str))

    to_do_i = 0
    to_dos = list(ToDo.live.done_by_user_in_date_range(
        user, from_date, to_date).order_by('done'))
    self.total = 0.0

    if not trackeds and not to_dos:
      return

    show_project = not project
    on_work_session = None
    while tracked_i < len(trackeds) or to_do_i < len(to_dos):
      if tracked_i >= len(trackeds) or (
          to_do_i < len(to_dos) and (
              trackeds[tracked_i].get_started(tz_str=tz_str) > (
                  to_dos[to_do_i].done))):
        if not on_work_session:
          raise Exception(
              'How did I pull a to do which occured before any of the '
              'trackeds?')
        to_do = to_dos[to_do_i]
        to_do_i += 1
        if to_do.project == project or not project:
          on_work_session.to_do_descriptions.append(
              self._to_do_description(to_do, show_project))
      else:
        tracked = trackeds[tracked_i]
        tracked_i += 1
        if tracked.project == project or not project:
          on_work_session = WorkSession(
              self._time_description(tracked, show_project), [])
          self.work_sessions.append(on_work_session)
          if tracked.hours:
            self.total += tracked.hours

    self.work_sessions.reverse()

  def _time_description(self, tracked, show_project):
    description = tracked.describe_time_span(self.tz_str)
    if show_project:
      description = '{} {}'.format(tracked.project.name, description)
    return description

  def _to_do_description(self, to_do, show_project):
    description = to_do.description
    if show_project:
      description = '{} {}'.format(to_do.project.name, description)
    return description

  def as_html(self):
    template = loader.get_template('time_breakdown.html')
    context = {
        'work_sessions': self.work_sessions,
        'project': self.project,
        'total': round(self.total, 2)}
    return template.render(context)


WorkSession = namedtuple('WorkSession', 'time_description to_do_descriptions')
