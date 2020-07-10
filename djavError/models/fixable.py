from django.db import models
from djaveAllowed.models import Allowed


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
