from django.contrib.auth.models import User
from django.db import models

from tracktime.models.project import Project


def get_latest_project(user):
  latest_project = LatestProject.objects.filter(user=user).first()
  if latest_project:
    return latest_project.project


def set_latest_project(user, project):
  latest_project = LatestProject.objects.filter(user=user).first()
  if latest_project:
    latest_project.project = project
  else:
    latest_project = LatestProject(user=user, project=project)
  latest_project.save()


class LatestProject(models.Model):
  """ Remember the latest project a user started the clock on. """
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
