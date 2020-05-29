from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable, PublishableManager
from djaveDT import beginning_of_day

from tracktime.models.project import Project


DELETED = 'DELETED'
DONE = 'DONE'
OPEN = 'OPEN'


class ToDoManager(PublishableManager):
  def not_done(self, creator, project=None):
    filtered = self.filter(done=None, creator=creator).select_related(
        'project', 'creator').order_by('-pk')
    if project:
      filtered = filtered.filter(project=project)
    return filtered

  def done_by_user_in_date_range(
      self, done_by, from_date, to_date, tz_str=None):
    from_dt = beginning_of_day(from_date, tz_str=tz_str)
    to_dt = beginning_of_day(to_date + timedelta(days=1), tz_str=tz_str)
    return self.filter(
        done_by=done_by, done__gte=from_dt, done__lte=to_dt).select_related(
        'project', 'creator', 'done_by').order_by('-pk')


class ToDo(Publishable):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True, help_text=(
      'When, if ever, was this ToDo marked done?'))
  project = models.ForeignKey(Project, on_delete=models.PROTECT, help_text=(
      'What project does this ToDo apply to?'))
  creator = models.ForeignKey(
      User, on_delete=models.PROTECT, related_name='creator', help_text=(
          'Who created this ToDo?'))
  done_by = models.ForeignKey(
      User, on_delete=models.PROTECT, related_name='done_by', null=True,
      blank=True, help_text='Who completed this ToDo?')

  live = ToDoManager()

  @classmethod
  def allowed(cls, api_key):
    if isinstance(api_key, UserAPIKey):
      return cls.all.filter(Q(creator=api_key.user) | Q(done_by=api_key.user))
    else:
      raise Exception(
          'I do not know how to handle {} api keys'.format(api_key.__class__))

  def explain_why_invalid(self):
    if int(bool(self.done)) + int(bool(self.done_by)) == 1:
      return ((
          'A done ToDo should say done_by and done. You specified '
          '{} and {} respectively').format(self.done, self.done_by))

  @classmethod
  def model_description(cls):
    return """
        A ToDo is a single task that a user intends to complete. Picking these
        is a bit of an art form. Ideally, you click "Done" on a few ToDos every
        ProjectWorkSession. Then when you Report, you can see a steady rhythm.
        """
