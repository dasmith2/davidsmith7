from djaveHTML.field import SelectField, PositiveFloatField, Option

from tracktime.models.project import Project
from tracktime.models.latest_project import get_latest_project


# I do `project_id` instead of `project` because that makes this line from
# invoice_rule_table work correctly:
# self.instance.__dict__.update(self.form.to_dict())

PROJECT = 'project'


def project_field(
    user, label=None, required=True, use_clock=None, has_to_do_list=None,
    has_invoices=None):
  """ use_clock can be True, False, or None, meaning you only want projects
  that use the clock, or don't, or it doesn't matter, respectively. """
  default = None
  if user and required:
    latest_project = get_latest_project(user)
    if latest_project:
      default = latest_project.pk
  options = project_options(
      user, use_clock=use_clock, has_to_do_list=has_to_do_list,
      has_invoices=has_invoices)
  field = SelectField(
      key_prefix=PROJECT, options=options,
      required=required, default=default, label=label, query_key='project')
  return field


def project_options(
    user, use_clock=None, has_to_do_list=None, has_invoices=None):
  projects = Project.live.allowed_by_user(user).order_by('name')
  if use_clock in (True, False):
    projects = projects.filter(use_clock=use_clock)
  if has_to_do_list in (True, False):
    projects = projects.filter(has_to_do_list=has_to_do_list)
  if has_invoices in (True, False):
    projects = projects.filter(has_invoices=has_invoices)
  return [Option(project.pk, project.name) for project in projects]


def hours_field():
  return PositiveFloatField(
      key_prefix='hours', required=True, default=0.0)
