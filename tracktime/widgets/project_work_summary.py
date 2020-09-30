from datetime import date

from django.shortcuts import reverse
from djaveDT import add_months
from djaveCRUDTable.columns import DisplayFieldColumn
from djaveCRUDTable.crud_table import CRUDTable
from djaveCRUDTable.filters import from_filter, to_filter
from djaveURL import dict_as_query

from tracktime.models.project import Project
from tracktime.models.project_to_do import ProjectToDo
from tracktime.models.project_work_session import ProjectWorkSession


class ProjectWorkSummary(CRUDTable):
  def __init__(self, user):
    display_columns = [DisplayFieldColumn('Project')]

    show_hours = False
    show_done = False
    for project in Project.allowed_by_user_live(user):
      show_hours = show_hours or project.use_clock
      show_done = show_done or project.has_to_do_list
    if show_hours:
      display_columns.append(DisplayFieldColumn('Hours'))
    if show_done:
      display_columns.append(DisplayFieldColumn('Done'))

    visible_filters = [
        from_filter('work_from', default=add_months(date.today(), -1)),
        to_filter('work_from')]
    super().__init__(
        Project, display_columns, visible_filters=visible_filters,
        list_url=reverse('project_work_summary'), can_create_new=False,
        list_header=None, list_api_url=reverse('project_work_summary_data'))


def get_what_i_did_per_projects(
    user, work_from, work_to, current_query_dict):
  projects = {}
  work_sessions = ProjectWorkSession.live.done_by_user_and_date_range(
      user, work_from.date(), work_to.date())
  for work_session in work_sessions:
    if work_session.hours:
      if work_session.project not in projects:
        projects[work_session.project] = WhatIDidPerProject(
            work_session.project, current_query_dict)
      projects[work_session.project].hours = round(
          projects[work_session.project].hours + work_session.hours, 2)
  to_dos = ProjectToDo.live.allowed_by_user(user).select_related(
      'project').filter(done__gte=work_from, done__lte=work_to)
  for to_do in to_dos:
    if to_do.project not in projects:
      projects[to_do.project] = WhatIDidPerProject(
          to_do.project, current_query_dict)
    projects[to_do.project].done += 1
  return sorted(list(projects.values()), key=lambda x: x.name)


class WhatIDidPerProject(object):
  def __init__(self, project, current_query_dict):
    self.project = project
    self.name = project.name
    self.hours = 0.0
    self.done = 0
    # This is why the WhatIDidPerProject filters should be exactly the same as
    # the WorkReport filters, except time breakdown is also by project.
    use_query_dict = {'project': project.pk}
    use_query_dict.update(current_query_dict)
    self.breakdown_url = reverse(
        'project_work_report') + dict_as_query(use_query_dict)
