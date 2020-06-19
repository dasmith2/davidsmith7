from django.db import models

from djavError.models import Error
from djaveClassMagic import RmOldManager


class LoggedCommandManager(RmOldManager):
  pass


class LoggedCommand(models.Model):
  command_name = models.CharField(max_length=200)
  started = models.DateTimeField()
  completed = models.DateTimeField(null=True, blank=True)
  error = models.ForeignKey(
      Error, null=True, blank=True, on_delete=models.CASCADE)
  created = models.DateTimeField(auto_now_add=True)

  objects = LoggedCommandManager()

  class Meta:
    ordering = ('-started',)
