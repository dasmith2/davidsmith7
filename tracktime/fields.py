from djaveForm.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.latest_project import get_latest_project


def project_field(user, work_session=None):
  # If you're creating a new one, set work_session to None.
  default = None
  latest_project = get_latest_project(user)
  if latest_project:
    default = latest_project.pk
  field = SelectField(
      key_prefix='project', options=project_options(), required=True,
      default=default)
  if work_session:
    field.set_value(work_session.project.pk)
    field.pk = work_session.pk
  return field


def project_options():
  projects = Project.live.order_by('name')
  return [Option(project.pk, project.name) for project in projects]


def hours_field(work_session):
  field = PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
  if work_session:
    field.set_value(work_session.hours)
    field.pk = work_session.pk
  return field
