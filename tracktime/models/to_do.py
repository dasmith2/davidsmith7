""" I realize now that these should be called Tasks and that "To Do" is a
phrase that should refer to undone Tasks for a particular project. But
ProjectToDo already inherits from ToDo, and the Django migration tools can't
handle renaming base classes without quite a lot of effort, and renaming ToDo
to Task won't actually accomplish much, so I will reluctantly let it stand. """
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.models.publishable import Publishable, LivePublishableManager
from djaveDT import beginning_of_day, now
from djaveHTML.field import SelectField, Option


DONE = 'Done'
NOT_DONE = 'Not done'


def get_status_filter(default=None):
  key_to_value = {NOT_DONE: True, DONE: False}
  options = [
      Option(key_to_value[NOT_DONE], NOT_DONE),
      Option(key_to_value[DONE], DONE)]
  use_default = None
  if default:
    use_default = key_to_value[default]
  return SelectField(
      key_prefix='to_do_status', options=options, required=False,
      label='Status', default=use_default, query_key='done__isnull')


class ToDoManager(LivePublishableManager):
  def order_for_doing(self, qs):
    return qs.select_related(
        *self.select_related_list()).order_by('-done', '-pk')

  def order_for_all(self, qs):
    return qs.select_related(
        *self.select_related_list()).order_by('-pk')

  def filter_not_long_done(self, qs, nnow=None):
    """ This is what shows in tracktime.widgets.to_dos_table. If you did
    something recently, it still shows. """
    nnow = nnow or now()
    return qs.filter(Q(done=None) | Q(done__gte=nnow - timedelta(days=1)))

  def filter_created(self, qs, from_date, to_date, tz_str=None):
    (from_dt, to_dt) = self._from_dt_to_dt(from_date, to_date, tz_str=tz_str)
    return qs.filter(created__gte=from_dt, created__lte=to_dt)

  def filter_done(self, qs, from_date, to_date, tz_str=None):
    (from_dt, to_dt) = self._from_dt_to_dt(from_date, to_date, tz_str=tz_str)
    return qs.filter(done__gte=from_dt, done__lte=to_dt)

  def filter_status(self, qs, status):
    if status == DONE:
      return qs.filter(done__isnull=False)
    elif status == NOT_DONE:
      return qs.filter(done__isnull=True)
    raise Exception(status)

  def _from_dt_to_dt(self, from_date, to_date, tz_str=None):
    return (
        beginning_of_day(from_date, tz_str=tz_str),
        beginning_of_day(to_date + timedelta(days=1), tz_str=tz_str))

  def select_related_list(self):
    return ['creator']


class ToDo(Publishable):
  description = models.TextField(help_text=(
      'Describe what you intend to do, or what you did.'))
  created = models.DateTimeField(auto_now_add=True, db_index=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True, help_text=(
      'When, if ever, was this marked done?'))
  creator = models.ForeignKey(
      User, on_delete=models.PROTECT, related_name='creator', help_text=(
          'Who created this?'))

  live = ToDoManager()

  @classmethod
  def filter_allowed_by_user(cls, user, query_set):
    return query_set.filter(creator=user)

  def allowed_api_keys(self, api_key_type):
    if api_key_type is UserAPIKey:
      return UserAPIKey.objects.filter(user=self.creator)

  @classmethod
  def model_description(cls):
    return """
        A ToDo is a single task that a user intends to complete. Picking these
        is a bit of an art form. Ideally, you click "Done" on a few ToDos every
        WorkSession. Then when you Report, you can see a steady rhythm.
        """
