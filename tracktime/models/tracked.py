from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djaveDT import now
from djaveNav import date_to_url_str

from tracktime.models.project import Project


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
    for key in totals:
      use_format = '({} hrs)'
      if totals[key] == 1:
        use_format = '({} hr)'
      totals[key] = use_format.format(totals[key])
    return totals

  def currently_tracking_project(self, user, nnow=None):
    nnow = nnow or now()
    tracking = self.filter(
        user=user, date=nnow.date(), started__isnull=False,
        stopped__isnull=True).select_related('project').first()
    if tracking:
      return tracking.project

  def get_unpunched(self, user, nnow=None):
    # Don't bother looking back over a week. There's not much point to drawing
    # the user's attention to ancient unpunched time.
    nnow = nnow or now()
    return self.filter(
        user=user, started__isnull=False,
        stopped__isnull=True,
        date__gte=nnow.date() - timedelta(days=7)).select_related('project')

  def get_can_punch_out(self, user, nnow=None):
    nnow = nnow or now()
    for tracked in self.get_unpunched(user, nnow=nnow):
      if nnow.date() == tracked.date:
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
    if self.stopped:
      raise Exception(
          'You can not stop a Tracked that is already stopped {}'.format(
              self.pk))
    if not self.started:
      raise Exception(
          'I can not stop a Tracked that was never started {}'.format(self.pk))
    if nnow < self.started:
      raise Exception((
          'How can I stop a Tracked that was started in the '
          'future? {}').format(self.pk))
    self.stopped = nnow
    self.hours = self._calculate_hours(self.stopped)
    self.save()

  def can_punch_out(self, nnow=None):
    nnow = nnow or now()
    return self.started and not self.stopped and self.date == nnow.date()

  def abandoned(self, nnow=None):
    return self.started and not self.stopped and (
        not self.can_punch_out(nnow=nnow))

  def _calculate_hours(self, stopped):
    delta = stopped - self.started
    return round(delta.total_seconds() / 3600, 2)

  def started_basically_equals(self, stopped):
    return 0.08 > self._calculate_hours(stopped)

  def __repr__(self):
    return '<Tracked {}: {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.project.name,
        self.date, self.hours)

  def __str__(self):
    return self.__repr__()

  objects = TrackedManager()
