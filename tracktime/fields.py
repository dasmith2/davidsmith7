from djaveForm.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.latest_project import get_latest_project


# I do `project_id` instead of `project` because that makes this line from
# invoice_rule_table work correctly:
# self.instance.__dict__.update(self.form.to_dict())

PROJECT = 'project'


def project_field(user=None, label=None, required=True):
  default = None
  if user and required:
    latest_project = get_latest_project(user)
    if latest_project:
      default = latest_project.pk
  field = SelectField(
      key_prefix=PROJECT, options=project_options(user), required=required,
      default=default, label=label)
  return field


def project_options(user):
  projects = Project.live.allowed_by_user(user).order_by('name')
  return [Option(project.pk, project.name) for project in projects]


def hours_field():
  return PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
