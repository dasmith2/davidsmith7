from datetime import timedelta

from django.db import models
from djaveAllowed.models import Allowed
from djaveDT import now, end_of_day, beginning_of_day


USE_DEFAULT = 'use_default'


class Fixable(Allowed):
  count = models.PositiveIntegerField(default=0)
  created = models.DateTimeField(auto_now_add=True)
  latest = models.DateTimeField()
  fixed = models.DateTimeField(null=True, blank=True, help_text=(
      'When, if ever, was this problem fixed?'))

  def save(self, *args, **kwargs):
    # This is important because a few things divide by count to get an average.
    if not self.count:
      raise Exception(
          'How am I creating a {} with no count?'.format(self.__class__))
    super().save(*args, **kwargs)

  class Meta:
    abstract = True


def get_last_week_unfixed_count(model, nnow=None):
  nnow = nnow or now()
  from_date = nnow - timedelta(days=7)
  to_date = nnow.date()
  return model.objects.filter(
      latest__gte=beginning_of_day(from_date),
      latest__lte=end_of_day(to_date),
      fixed__isnull=True).count()
