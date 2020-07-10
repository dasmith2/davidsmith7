from datetime import timedelta

from django.db import models
from djaveClassMagic import RmOldManager
from djavError.models.problem_request import ProblemRequest
from djaveDT import now


class LongRequestManager(RmOldManager):
  def log_long_request(self, path, duration, method, variables, nnow=None):
    nnow = nnow or now()
    existing = self.filter(
        path=path, method=method,
        created__gte=now() - timedelta(days=1)).first()
    if existing:
      existing.total_duration += duration
      existing.latest = now()
      existing.count += 1
      existing.save()
      return existing
    return self.create(
        path=path,
        total_duration=duration,
        method=method,
        variables=variables,
        latest=now(),
        count=1)


class LongRequest(ProblemRequest):
  """ Requests that took too long. """
  total_duration = models.FloatField(help_text=('In seconds.'))

  objects = LongRequestManager()

  def increment(self, duration):
    self.total_duration += duration
    super().increment()

  def average_duration(self):  # In seconds.
    if self.count == 0:
      return 'DIVIDE BY ZERO'
    return self.total_duration / self.count

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    if user.is_superuser:
      return query_set
    return query_set.none()

  class Meta:
    ordering = ('-created',)
