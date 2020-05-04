from django.contrib.auth.models import User
from django.db import models
from djaveDT import now

from tracktime.models.work_type import WorkType
from tracktime.models.project import Project


class TrackedManager(models.Manager):
  def currently_tracking_project(self, user, nnow=None):
    nnow = nnow or now()
    tracking = self.filter(
        user=user, date=nnow.date(), started__isnull=False,
        stopped__isnull=True).select_related('project').first()
    if tracking:
      return tracking.project


class Tracked(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  work_type = models.ForeignKey(WorkType, on_delete=models.PROTECT)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  date = models.DateField()
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

  def _calculate_hours(self, stopped):
    delta = stopped - self.started
    return round(delta.total_seconds() / 3600, 2)

  def started_basically_equals(self, stopped):
    return 0.08 > self._calculate_hours(stopped)

  def __repr__(self):
    return '<Tracked {}: {} {} {} {} for {} hrs>'.format(
        self.pk, self.user.username, self.work_type.name, self.project.name,
        self.date, self.hours)

  def __str__(self):
    return self.__repr__()

  objects = TrackedManager()
