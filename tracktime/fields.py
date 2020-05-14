from djaveForm.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.latest_project import get_latest_project


def project_field(user, tracked=None):
  # If you're creating a new one, set tracked to None.
  default = None
  latest_project = get_latest_project(user)
  if latest_project:
    default = latest_project.pk
  field = SelectField(
      key_prefix='project', options=project_options(), required=True,
      default=default)
  if tracked:
    field.set_value(tracked.project.pk)
    field.pk = tracked.pk
  return field


def project_options():
  projects = Project.live.order_by('name')
  return [Option(project.pk, project.name) for project in projects]


def hours_field(tracked):
  field = PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
  if tracked:
    field.set_value(tracked.hours)
    field.pk = tracked.pk
  return field
