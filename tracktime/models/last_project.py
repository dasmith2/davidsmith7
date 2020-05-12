from django.contrib.auth.models import User
from django.db import models

from tracktime.models.project import Project


class LatestProject(models.Model):
  """ Remember the latest project a user started the clock on. """
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
