from djaveForm.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.latest_project import get_latest_project


PROJECT = 'project'


def project_field(user=None, label=None):
  default = None
  if user:
    latest_project = get_latest_project(user)
    if latest_project:
      default = latest_project.pk
  field = SelectField(
      key_prefix=PROJECT, options=project_options(), required=True,
      default=default, label=label)
  return field


def project_options():
  projects = Project.live.order_by('name')
  return [Option(project.pk, project.name) for project in projects]


def hours_field():
  return PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
