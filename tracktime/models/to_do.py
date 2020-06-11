from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable, PublishableManager
from djaveDT import beginning_of_day, now


DELETED = 'DELETED'
DONE = 'DONE'
OPEN = 'OPEN'


class ToDoManager(PublishableManager):
  def not_long_done(self, creator, nnow=None):
    """ This is what shows in tracktime.widgets.to_do_table. If you did
    something recently, it still shows. """
    nnow = nnow or now()
    return self.filter(
        Q(done=None) | Q(done__gte=nnow - timedelta(days=1)),
        creator=creator).select_related(
            *self.select_related_list()).order_by('-done', '-pk')

  def done_by_user_in_date_range(
      self, done_by, from_date, to_date, tz_str=None):
    from_dt = beginning_of_day(from_date, tz_str=tz_str)
    to_dt = beginning_of_day(to_date + timedelta(days=1), tz_str=tz_str)
    return self.filter(
        done_by=done_by, done__gte=from_dt, done__lte=to_dt).select_related(
        *self.select_related_list()).order_by('-pk')

  def select_related_list(self):
    return ['creator', 'done_by']


class ToDo(Publishable):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True, help_text=(
      'When, if ever, was this ToDo marked done?'))
  creator = models.ForeignKey(
      User, on_delete=models.PROTECT, related_name='creator', help_text=(
          'Who created this ToDo?'))
  done_by = models.ForeignKey(
      User, on_delete=models.PROTECT, related_name='done_by', null=True,
      blank=True, help_text='Who completed this ToDo?')

  live = ToDoManager()

  @classmethod
  def allowed_by_user(cls, user):
    return cls.all.filter(Q(creator=user) | Q(done_by=user))

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      users = set([self.creator])
      if self.done_by:
        users.add(self.done_by)
      return UserAPIKey.objects.filter(user__in=users)
    else:
      raise Exception('I dont know which {} are allowed'.format(
          api_key_type.__class__))

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
        WorkSession. Then when you Report, you can see a steady rhythm.
        """
