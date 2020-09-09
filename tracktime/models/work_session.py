""" All this class knows about is a user tracking time. But you probably want
to track time against something specific, so you'll probably inherit from these
classes. See tracktime.models.project_work_session as an example. """
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable, LivePublishableManager
from djaveDT import (
    now, d_to_str, time_to_time_str, tz_dt_to_tz_dt,
    tz_dt_to_str, beginning_of_day, dt_to_time_str)
from djaveNav import date_to_url_str


# If a WorkSession isn't stopped within 16 hours it's considered abandoned.
ABANDONED_AFTER_HOURS = 16

DELETED = 'DELETED'
DONE = 'DONE'
ABANDONED = 'ABANDONED'
IN_PROGRESS = 'IN_PROGRESS'


class WorkSessionManager(LivePublishableManager):
  def done_by_user_and_date(self, user, date, nnow=None):
    return self.done_by_user_and_date_range(user, date, date, nnow=nnow)

  def done_by_user_and_date_range(self, user, from_date, to_date, nnow=None):
    to_return = self.filter(
        Q(started__isnull=True) | Q(stopped__isnull=False),
        user=user).select_related(*self.select_related_list()).order_by('-pk')
    if from_date:
      to_return = to_return.filter(date__gte=from_date)
    if to_date:
      to_return = to_return.filter(date__lte=to_date)
    return to_return

  def select_related_list(self):
    return ['user']

  def total_hours_per_date(self, start_date, end_date, user):
    if start_date > end_date:
      raise Exception('{} > {}'.format(start_date, end_date))
    got_work_session = self.filter(
        date__gte=start_date, date__lte=end_date, user=user).order_by('date')
    on_date = start_date
    totals = {date_to_url_str(on_date): 0.0}
    for work_session in got_work_session:
      while work_session.date > on_date:
        on_date += timedelta(days=1)
        totals[date_to_url_str(on_date)] = 0.0
      if work_session.hours:
        totals[date_to_url_str(work_session.date)] += work_session.hours
    while on_date < end_date:
      on_date += timedelta(days=1)
      totals[date_to_url_str(on_date)] = 0.0
    for key in totals:
      use_format = '({} hrs)'
      if totals[key] == 1:
        use_format = '({} hr)'
      totals[key] = use_format.format(round(totals[key], 2))
    return totals

  def get_clock_never_stopped(self, user, nnow=None):
    # A week old clock that wasn't stopped isn't running, it's abandoned. Don't
    # bother looking back over a week. There's not much point to drawing the
    # user's attention to ancient unpunched time.
    nnow = nnow or now()
    return self.filter(
        user=user, started__isnull=False,
        stopped__isnull=True,
        date__gte=nnow.date() - timedelta(days=7)).order_by(
            'pk').select_related(*self.select_related_list())

  def get_clock_running(self, user, nnow=None):
    # By clock running I mean specifically the WorkSession whose clock can be
    # stopped.
    nnow = nnow or now()
    for work_session in self.get_clock_never_stopped(user, nnow=nnow):
      if work_session.clock_running(nnow=nnow):
        return work_session


class WorkSession(Publishable):
  user = models.ForeignKey(User, on_delete=models.PROTECT, help_text=(
      'Which User actually did the work?'))
  date = models.DateField(db_index=True, help_text=(
      'What date did this happen on? If a '
      'User in New York punches out at 11pm on Friday, the '
      'stopped field is technically stored as 3 or 4am Greenwich '
      'Mean Time, but the date field here will say Friday.'))
  hours = models.FloatField(blank=True, null=True, help_text=(
      'How long was this session in hours? If hours is null, then '
      'the session is ongoing or abandoned.'))
  started = models.DateTimeField(blank=True, null=True, help_text=(
      'If the User used the clock to time this session, when did they '
      'start the clock?'))
  stopped = models.DateTimeField(blank=True, null=True, help_text=(
      'If the User used the clock to time this work session, when did they '
      'stop the clock?'))

  def explain_why_invalid(self):
    if self.started is None and self.hours is None:
      return (
          'You have to specify hours, meaning a completed work session, or '
          'started, meaning a started work session. It is pointless to create '
          'a work session with neither a start time nor a duration.')
    if self.stopped:
      if self.started:
        if self.started > self.stopped:
          return 'started should be <= stopped'
      else:
        return (
            'If you say when a work session stopped, you have to say when it '
            'started too')
    if self.started and self.hours and not self.stopped:
      return (
          'If a work session has a start time and hours, it must have a '
          'stop time')

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(user=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.user)

  def describe_time_span_for_invoices(self, tz_str=None):
    if self.started and self.stopped:
      started = self.get_started(tz_str=tz_str)
      stopped = tz_dt_to_tz_dt(self.stopped, tz_str=tz_str)
      from_string = tz_dt_to_str(started)
      if started.date() == stopped.date():
        to_string = time_to_time_str(stopped.time())
      else:
        to_string = tz_dt_to_str(stopped)
      return '{} to {}, {} hours'.format(
          from_string, to_string, round(self.hours, 2))
    elif self.date and self.hours:
      return '{}, {} hours'.format(
          d_to_str(self.date), round(self.hours, 2))
    elif self.clock_running():
      started = self.get_started(tz_str=tz_str)
      return '{}, still working'.format(tz_dt_to_str(started))

  def describe_time_span_for_time_entry(self):
    if self.started:
      return '{} starting at {}'.format(
          self.hours, dt_to_time_str(self.started))
    return self.hours

  def add_to_json(self, data):
    data['time_entry_description'] = self.describe_time_span_for_time_entry()

  def stop(self, nnow=None):
    nnow = nnow or now()
    why_not = self.explain_why_can_not_stop(nnow=nnow)
    if why_not:
      raise Exception(why_not)
    self.stopped = nnow
    self.hours = self._calculate_hours(self.stopped)
    self.save()

  def get_started(self, tz_str=None):
    return tz_dt_to_tz_dt(
        self.started or beginning_of_day(self.date, tz_str=tz_str),
        tz_str=tz_str)

  def clock_running(self, nnow=None):
    return self.started and not self.stopped and not self.abandoned(nnow=nnow)

  def abandoned(self, nnow=None):
    nnow = nnow or now()
    return self.started and not self.stopped and (
        self.started < nnow - timedelta(hours=ABANDONED_AFTER_HOURS))

  def explain_why_can_not_stop(self, nnow=None):
    nnow = nnow or now()
    if self.stopped:
      return 'The clock is already stopped on this work session'
    if not self.started:
      return 'The clock was never started on this work session'
    if self.deleted:
      return 'This work session was canceled or deleted'
    if nnow < self.started:
      return (
          'How can I stop a work session that was started in the '
          'future?!')
    if self.abandoned(nnow=nnow):
      return (
          'This work session appears to be abandoned because it '
          'was started over {} hours ago').format(ABANDONED_AFTER_HOURS)

  def can_stop(self, nnow=None):
    return not bool(self.explain_why_can_not_stop(nnow=nnow))

  def _calculate_hours(self, stopped):
    if self.deleted:
      raise Exception('I can not calculate hours for a deleted work session')
    delta = stopped - self.started
    return max([round(delta.total_seconds() / 3600, 2), 0.01])

  def __repr__(self, nnow=None):
    return '<WorkSession {}: {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.date, self.status(nnow=nnow),
        self.hours)

  def __str__(self, nnow=None):
    return self.__repr__(nnow=nnow)

  def status(self, nnow=None):
    nnow = nnow or now()
    if self.deleted:
      return DELETED
    elif self.stopped:
      return DONE
    elif self.started:
      if self.abandoned(nnow=nnow):
        return ABANDONED
      return IN_PROGRESS
    elif self.hours:
      return DONE
    raise Exception('I cant figure out what status {} is'.format(self.pk))

  live = WorkSessionManager()
