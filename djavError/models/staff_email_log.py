from django.db import models
from djaveAllowed.models import Allowed


class StaffEmailLog(Allowed):
  title = models.CharField(max_length=250)
  created = models.DateTimeField(auto_now_add=True)
  latest = models.DateTimeField()
  count = models.PositiveIntegerField(default=0)
  message = models.TextField(blank=True, default='')
  to = models.TextField(blank=True, default='')

  @classmethod
  def filter_live(cls, query_set):
    return query_set

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    if user.is_superuser:
      return query_set
    return query_set.none()

  class Meta:
    abstract = True
