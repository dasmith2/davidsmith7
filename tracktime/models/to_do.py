from django.db import models

from tracktime.models.project import Project


class ToDoManager(models.Manager):
  def not_checked_off(self, user, project):
    return self.filter(
        checked_off=None, user=user, project=project).order_by('sort_order')


class ToDo(models.Model):
  description = models.TextField()
  created = models.DateTimeField(auto_now_add=True)
  checked_off = models.DateTimeField(null=True, blank=True, db_index=True)
  project = models.ForeignKey(Project, on_delete=models.PROTECT)
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  sort_order = models.PositiveIntegerField()

  objects = ToDoManager()
