from djaveForm.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.work_type import WorkType


def work_type_field(tracked=None):
  # If you're creating a new one, set tracked to None.
  field = SelectField(
      key_prefix='work_type', options=work_type_options(), required=True)
  if tracked:
    field.set_value(tracked.work_type.pk)
    field.pk = tracked.pk
  return field


def work_type_options():
  work_types = WorkType.objects.order_by('name')
  return [Option(work_type.pk, work_type.name) for work_type in work_types]


def project_field(tracked=None):
  # If you're creating a new one, set tracked to None.
  field = SelectField(
      key_prefix='project', options=project_options(), required=True)
  if tracked:
    field.set_value(tracked.project.pk)
    field.pk = tracked.pk
  return field


def project_options():
  projects = Project.objects.order_by('name')
  return [Option(project.pk, project.name) for project in projects]


def hours_field(tracked):
  field = PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
  if tracked:
    field.set_value(tracked.hours)
    field.pk = tracked.pk
  return field
