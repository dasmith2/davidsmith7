from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.published import Published, PublishedManager
from djaveDT import dt_for_json, beginning_of_day

from tracktime.models.project import Project


DELETED = 'DELETED'
DONE = 'DONE'
OPEN = 'OPEN'


class ToDoManager(PublishedManager):
  def not_done(self, user, project=None):
    filtered = self.filter(
        done=None, user=user).select_related('project').order_by('-pk')
    if project:
      filtered = filtered.filter(project=project)
    return filtered

  def done_by_user_in_date_range(self, user, from_date, to_date, tz_str=None):
    from_dt = beginning_of_day(from_date, tz_str=tz_str)
    to_dt = beginning_of_day(to_date + timedelta(days=1), tz_str=tz_str)
    return self.filter(
        user=user, done__gte=from_dt, done__lte=to_dt).select_related(
        'project', 'user').order_by('-pk')


class ToDo(Published):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  user = models.ForeignKey(User, on_delete=models.PROTECT)

  live = ToDoManager()

  def status(self):
    if self.deleted:
      return DELETED
    if self.done:
      return DONE
    return OPEN

  def as_json(self):
    return dict(
        pk=self.pk,
        description=self.description,
        created=dt_for_json(self.created),
        deleted=dt_for_json(self.deleted),
        done=dt_for_json(self.done),
        project=self.project.pk,
        user=self.user.pk,
        status=self.status())
