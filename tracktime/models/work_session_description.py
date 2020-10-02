from collections import namedtuple

from djaveDT import beginning_of_day
from djavError.log_error import log_error

from tracktime.models.to_do import ToDo
from tracktime.models.work_session import WorkSession


WorkSessionDescription = namedtuple(
    'WorkSessionDescription',
    'work_session time_description hours to_do_descriptions')


class WorkSessionDescriptions(object):
  def __init__(self, user, from_dt, to, tz_str):
    """ from_dt is optional so derived classes can pull back all unbilled
    descriptions. """
    self.user = user
    self.from_dt = from_dt
    self.to = to
    self.tz_str = tz_str

    self._calc_work_session_descriptions()

  def has_work_session_descriptions(self):
    return bool(self.get_work_session_descriptions())

  def first_date(self):
    if self.has_work_session_descriptions():
      return self.get_work_session_descriptions()[0]

  def get_work_session_descriptions(self):
    return self._work_session_descriptions

  def earliest_date(self):
    descriptions = self.get_work_session_descriptions()
    if not descriptions:
      raise Exception(
          'There are no work sessions so I cant tell you when the earliest '
          'was. Check has_work_session_descriptions first.')
    earliest = None
    for description in descriptions:
      if not earliest or earliest > description.work_session.date:
        earliest = description.work_session.date
    return earliest

  def get_total_hours(self):
    total_hours = 0.0
    for wsd in self.get_work_session_descriptions():
      total_hours += wsd.work_session.hours
    return total_hours

  def _calc_work_session_descriptions(self):
    self._work_session_descriptions = []

    work_session_i = 0
    work_sessions = list(self.get_work_sessions())
    work_sessions.sort(key=lambda x: x.get_started())

    to_do_i = 0
    to_dos = list(self.get_to_dos(work_sessions))
    to_dos.sort(key=lambda x: x.done)

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
              None, '(marked done outside a work session)', 0, [])
          self._work_session_descriptions.append(on_work_session)
          log_error(
              'How does a to do not have a work session?',
              str(self.list_params()))
        to_do = to_dos[to_do_i]
        to_do_i += 1
        on_work_session.to_do_descriptions.append(
            self.to_do_description(to_do))
      else:
        work_session = work_sessions[work_session_i]
        work_session_i += 1
        on_work_session = WorkSessionDescription(
            work_session, self.time_description(work_session),
            work_session.hours, [])
        self._work_session_descriptions.append(on_work_session)

    self._work_session_descriptions.reverse()

  def work_session_class(self):
    return WorkSession

  def _work_session_class(self):
    if not issubclass(self.work_session_class(), WorkSession):
      raise Exception(
          'work_session_class should return a subclass of WorkSession')
    return self.work_session_class()

  def get_work_sessions(self):
    return self._work_session_class().live.done_by_user_and_date_range(
        self.user, self.from_dt, self.to)

  def to_do_class(self):
    return ToDo

  def _to_do_class(self):
    if not issubclass(self.to_do_class(), ToDo):
      raise Exception('to_do_class should return a subclass of ToDo')
    return self.to_do_class()

  def get_to_dos(self, work_sessions):
    manager = self._to_do_class().live
    if not work_sessions:
      return manager.none()

    # Don't use self.from_dt because that's optional.
    from_dt = beginning_of_day(
        min([work_session.date for work_session in work_sessions]))

    to_dos = manager.allowed_by_user(self.user)
    return manager.filter_done(to_dos, from_dt, self.to)

  def time_description(self, work_session):
    return work_session.describe_time_span_for_invoices(self.tz_str)

  def to_do_description(self, to_do):
    return to_do.description

  def list_params(self):
    return [self.user, self.from_dt, self.to, self.tz_str]
