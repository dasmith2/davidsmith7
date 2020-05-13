from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djaveDT import now, dt_for_json, d_for_json
from djaveNav import date_to_url_str

from tracktime.models.project import Project


# If a Tracked isn't stopped within 16 hours it's considered abandoned.
ABANDONED_AFTER_HOURS = 16
# If a Tracked was started less than 5 minutes ago, it should probably just be
# canceled.
TOO_FEW_MINUTES = 5


class TrackedManager(models.Manager):
  def total_hours_per_day(self, start_day, end_day, user):
    if start_day > end_day:
      raise Exception('{} > {}'.format(start_day, end_day))
    got_tracked = self.filter(
        date__gte=start_day, date__lte=end_day, user=user).order_by('date')
    on_day = start_day
    totals = {date_to_url_str(on_day): 0.0}
    for tracked in got_tracked:
      while tracked.date > on_day:
        on_day += timedelta(days=1)
        totals[date_to_url_str(on_day)] = 0.0
      if tracked.hours:
        totals[date_to_url_str(tracked.date)] += tracked.hours
    while on_day < end_day:
      on_day += timedelta(days=1)
      totals[date_to_url_str(on_day)] = 0.0
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


class Tracked(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  date = models.DateField(db_index=True)
  hours = models.FloatField(blank=True, null=True)
  started = models.DateTimeField(blank=True, null=True, help_text=(
      'When did the user start work?'))
  stopped = models.DateTimeField(blank=True, null=True, help_text=(
      'When did the user finish working?'))

  def stop(self, nnow=None):
    nnow = nnow or now()
    why_not = self.explain_why_can_not_stop(nnow=nnow)
    if why_not:
      raise Exception(why_not)
    self.stopped = nnow
    self.hours = self._calculate_hours(self.stopped)
    self.save()

  def clock_running(self, nnow=None):
    return self.started and not self.stopped and not self.abandoned(nnow=nnow)

  def abandoned(self, nnow=None):
    nnow = nnow or now()
    return not self.stopped and (
        self.started < nnow - timedelta(hours=ABANDONED_AFTER_HOURS))

  def explain_why_can_not_stop(self, nnow=None):
    nnow = nnow or now()
    if self.stopped:
      return 'The clock is already stopped on this work session'
    if not self.started:
      return 'The clock was never started on this work session'
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
    delta = stopped - self.started
    return round(delta.total_seconds() / 3600, 2)

  def __repr__(self):
    return '<Tracked {}: {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.project.name,
        self.date, self.hours)

  def __str__(self):
    return self.__repr__()

  objects = TrackedManager()

  def as_json(self):
    return dict(
        pk=self.pk,
        user=self.user.pk,
        project=self.project.pk,
        date=d_for_json(self.date),
        hours=self.hours,
        started=dt_for_json(self.started),
        stopped=dt_for_json(self.stopped))
