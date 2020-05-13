from django.contrib.auth.models import User
from django.db import models
from djaveDT import dt_for_json

from tracktime.models.project import Project


class ToDoManager(models.Manager):
  def not_done(self, user, project=None):
    filtered = self.filter(
        done=None, user=user).select_related('project').order_by('-pk')
    if project:
      filtered = filtered.filter(project=project)
    return filtered


class ToDo(models.Model):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  done = models.DateTimeField(null=True, blank=True, db_index=True)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  user = models.ForeignKey(User, on_delete=models.PROTECT)

  objects = ToDoManager()

  def as_json(self):
    return dict(
        pk=self.pk,
        description=self.description,
        created=dt_for_json(self.created),
        done=dt_for_json(self.done),
        project=self.project.pk,
        user=self.user.pk)
