from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.published import Published, PublishedManager
from djaveDT import (
    now, dt_for_json, d_for_json, d_to_str, time_to_time_str, tz_dt_to_tz_dt,
    tz_dt_to_str, beginning_of_day)
from djaveNav import date_to_url_str

from tracktime.models.project import Project


# If a Tracked isn't stopped within 16 hours it's considered abandoned.
ABANDONED_AFTER_HOURS = 16
# If a Tracked was started less than 5 minutes ago, it should probably just be
# canceled.
TOO_FEW_MINUTES = 5

DELETED = 'DELETED'
DONE = 'DONE'
ABANDONED = 'ABANDONED'
IN_PROGRESS = 'IN_PROGRESS'


class TrackedManager(PublishedManager):
  def by_user_and_date(self, user, date, nnow=None):
    return self.by_user_and_date_range(user, date, date, nnow=nnow)

  def by_user_and_date_range(self, user, from_date, to_date, nnow=None):
    to_return = []
    for tracked in self.filter(
        user=user, date__gte=from_date, date__lte=to_date).select_related(
            'project', 'user').order_by('-pk'):
      if not tracked.abandoned(nnow=nnow):
        to_return.append(tracked)
    return to_return

  def total_hours_per_date(self, start_date, end_date, user):
    if start_date > end_date:
      raise Exception('{} > {}'.format(start_date, end_date))
    got_tracked = self.filter(
        date__gte=start_date, date__lte=end_date, user=user).order_by('date')
    on_date = start_date
    totals = {date_to_url_str(on_date): 0.0}
    for tracked in got_tracked:
      while tracked.date > on_date:
        on_date += timedelta(days=1)
        totals[date_to_url_str(on_date)] = 0.0
      if tracked.hours:
        totals[date_to_url_str(tracked.date)] += tracked.hours
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
            'pk').select_related('project')

  def get_clock_running(self, user, nnow=None):
    # By clock running I mean specifically the Tracked whose clock can be
    # stopped.
    nnow = nnow or now()
    for tracked in self.get_clock_never_stopped(user, nnow=nnow):
      if tracked.clock_running(nnow=nnow):
        return tracked


class Tracked(Published):
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  date = models.DateField(db_index=True)
  hours = models.FloatField(blank=True, null=True)
  started = models.DateTimeField(blank=True, null=True, help_text=(
      'When did the user start work?'))
  stopped = models.DateTimeField(blank=True, null=True, help_text=(
      'When did the user finish working?'))

  def describe_time_span(self, tz_str=None):
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
    if self.started > nnow - timedelta(minutes=TOO_FEW_MINUTES):
      return (
          'This work session is less than {} minutes old. You '
          'should probably just cancel it.').format(TOO_FEW_MINUTES)

  def can_stop(self, nnow=None):
    return not bool(self.explain_why_can_not_stop(nnow=nnow))

  def _calculate_hours(self, stopped):
    if self.deleted:
      raise Exception('I can not calculate hours for a deleted work session')
    delta = stopped - self.started
    return round(delta.total_seconds() / 3600, 2)

  def __repr__(self, nnow=None):
    return '<Tracked {}: {} {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.project.name,
        self.date, self.hours, self.status(nnow=nnow))

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

  live = TrackedManager()

  def as_json(self, nnow=None):
    return dict(
        pk=self.pk,
        user=self.user.pk,
        project=self.project.pk,
        date=d_for_json(self.date),
        hours=self.hours,
        started=dt_for_json(self.started),
        stopped=dt_for_json(self.stopped),
        deleted=dt_for_json(self.deleted),
        status=self.status(nnow=nnow))

  class Meta:
    verbose_name = 'work session'
