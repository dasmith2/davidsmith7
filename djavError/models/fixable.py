from datetime import timedelta

from django.db import models
from djaveAllowed.models import Allowed
from djaveDT import now, end_of_day, beginning_of_day


USE_DEFAULT = 'use_default'
EITHER = 'either'
FIXED = 'fixed'
NOT_FIXED = 'not_fixed'


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


def get_fixables(
    model, from_date=USE_DEFAULT, to_date=USE_DEFAULT, status=USE_DEFAULT,
    nnow=None):
  """ Assumes you have a created column and a fixed column. Easiest thing is to
  inherit from djavError.models.fixable I'm leaving this here instead of in
  djavError.models.fixable because this function knows about UI specific
  filters and defaults. """
  nnow = nnow or now()
  if from_date == USE_DEFAULT:
    from_date = default_from_date(nnow=nnow)
  if to_date == USE_DEFAULT:
    to_date = nnow.date()
  query_set = model.objects.filter(
      created__gte=beginning_of_day(from_date),
      created__lte=end_of_day(to_date)).order_by('-created')
  return do_fixed_filter(query_set, status)


def do_fixed_filter(query_set, status):
  if status == USE_DEFAULT:
    status = default_status()
  if status and status != EITHER:
    query_set = query_set.filter(fixed__isnull=status != FIXED)
  return query_set


def default_status():
  return NOT_FIXED


def default_from_date(nnow=None):
  nnow = nnow or now()
  return nnow.date() - timedelta(days=7)
