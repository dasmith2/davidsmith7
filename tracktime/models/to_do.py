from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from djaveAPI.publishable import Publishable, PublishableManager
from djaveDT import beginning_of_day

from tracktime.models.project import Project


DELETED = 'DELETED'
DONE = 'DONE'
OPEN = 'OPEN'


class ToDoManager(PublishableManager):
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


class ToDo(Publishable):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True, help_text=(
      'When, if ever, was this ToDo marked done?'))
  project = models.ForeignKey(Project, on_delete=models.PROTECT, help_text=(
      'What project does this ToDo apply to?'))
  user = models.ForeignKey(User, on_delete=models.PROTECT)

  live = ToDoManager()

  def status(self):
    if self.deleted:
      return DELETED
    if self.done:
      return DONE
    return OPEN

  def model_description():
    return """
        A ToDo is a single task that a user intends to complete. Picking these
        is a bit of an art form. Ideally, you click "Done" on a few ToDos every
        ProjectWorkSession. Then when you Report, you can see a steady rhythm.
        """
