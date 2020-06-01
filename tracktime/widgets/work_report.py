from collections import namedtuple

from django.template import loader
from djaveReport.date_range_report import FROM_DATE, TO_DATE
from djaveURL import date_to_url_str

from tracktime.models.to_do import ToDo
from tracktime.models.work_session import WorkSession


def work_report_url_dict(from_date=None, to_date=None):
  query_dict = {}
  if from_date:
    query_dict[FROM_DATE] = date_to_url_str(from_date)
  if to_date:
    query_dict[TO_DATE] = date_to_url_str(to_date)
  return query_dict


class WorkReportContent(object):
  def __init__(self, user, from_date, to_date, tz_str=None):
    self.user = user
    self.from_date = from_date
    self.to_date = to_date
    self.tz_str = tz_str
    self.work_session_descriptions = self.get_work_session_descriptions()

  def get_work_session_descriptions(self):
    work_session_descriptions = []

    work_session_i = 0
    work_sessions = self.get_work_sessions()

    to_do_i = 0
    to_dos = self.get_to_dos()
    self.total = 0.0

    if not work_sessions and not to_dos:
      return

    on_work_session = None
    while work_session_i < len(work_sessions) or to_do_i < len(to_dos):
      if work_session_i >= len(work_sessions) or (
          to_do_i < len(to_dos) and (
              work_sessions[work_session_i].get_started(tz_str=self.tz_str) > (
                  to_dos[to_do_i].done))):
        if not on_work_session:
          on_work_session = WorkSessionDescription(
              '(marked done outside a work session)', [])
          work_session_descriptions.append(on_work_session)
        to_do = to_dos[to_do_i]
        to_do_i += 1
        on_work_session.to_do_descriptions.append(
            self.to_do_description(to_do))
      else:
        work_session = work_sessions[work_session_i]
        work_session_i += 1
        on_work_session = WorkSessionDescription(
            self.time_description(work_session), [])
        work_session_descriptions.append(on_work_session)
        if work_session.hours:
          self.total += work_session.hours

    work_session_descriptions.reverse()
    return work_session_descriptions

  def work_session_class(self):
    return WorkSession

  def _work_session_class(self):
    if not issubclass(self.work_session_class(), WorkSession):
      raise Exception(
          'work_session_class should return a subclass of WorkSession')
    return self.work_session_class()

  def get_work_sessions(self):
    work_sessions = list(
        self._work_session_class().live.done_by_user_and_date_range(
            self.user, self.from_date, self.to_date))
    work_sessions.sort(key=lambda x: x.get_started())
    return work_sessions

  def to_do_class(self):
    return ToDo

  def _to_do_class(self):
    if not issubclass(self.to_do_class(), ToDo):
      raise Exception('to_do_class should return a subclass of ToDo')
    return self.to_do_class()

  def get_to_dos(self):
    return list(self._to_do_class().live.done_by_user_in_date_range(
        self.user, self.from_date, self.to_date).order_by('done'))

  def time_description(self, work_session):
    return work_session.describe_time_span(self.tz_str)

  def to_do_description(self, to_do):
    return to_do.description

  def as_html(self):
    template = loader.get_template('work_report.html')
    context = {
        'work_session_descriptions': self.work_session_descriptions,
        'header': self.html_header()}
    return template.render(context)

  def html_header(self):
    total = round(self.total, 2)
    return 'Total: {} hours'.format(total)


WorkSessionDescription = namedtuple(
    'WorkSessionDescription', 'time_description to_do_descriptions')
