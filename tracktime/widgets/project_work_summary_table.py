from datetime import timedelta

from django.shortcuts import reverse
from djaveDT import now
from djaveHTML.cell_content import InHref
from djaveHTML.table import Table
from djaveReport.date_range_report import DateRangeReport
from djaveURL import dict_as_query

from tracktime.models.project import Project
from tracktime.models.project_to_do import ProjectToDo
from tracktime.models.project_work_session import ProjectWorkSession


class ProjectWorkSessionSummaryReport(DateRangeReport):
  def __init__(self, request_get, user, nnow=None):
    nnow = nnow or now()
    default_from_date = nnow.date() - timedelta(days=7)
    default_to_date = nnow.date()
    super().__init__(default_from_date, default_to_date, request_get)

    current_query_dict = self.get_query_dict()
    self.what_i_did_content = ProjectWorkSessionSummaryTable(
        user, self.from_date(), self.to_date(), current_query_dict)
    self.add_content(self.what_i_did_content)


class ProjectWorkSessionSummaryTable(Table):
  def __init__(self, user, from_date, to_date, current_query_dict):
    what_i_did_per_projects = self.get_what_i_did_per_projects(
        user, from_date, to_date, current_query_dict)

    do_hours = False
    do_done = False
    for project in Project.live.allowed_by_user(user):
      do_hours = do_hours or project.use_clock
      do_done = do_done or project.has_to_do_list

    headers = ['Project']
    if do_hours:
      headers.append('Hours')
    if do_done:
      headers.append('Done')
    super().__init__(headers)

    for what_i_did_per_project in what_i_did_per_projects:
      css_class = 'details_{}'.format(what_i_did_per_project.project.pk)
      cells = [what_i_did_per_project.name]
      if do_hours:
        hours_href = None
        if what_i_did_per_project.project.use_clock:
          hours_href = InHref(
              what_i_did_per_project.hours,
              what_i_did_per_project.breakdown_url, classes=[css_class])
        cells.append(hours_href)
      if do_done:
        cells.append(what_i_did_per_project.done)
      self.create_row(cells)

  def get_what_i_did_per_projects(
      self, user, from_date, to_date, current_query_dict):
    projects = {}
    work_sessions = ProjectWorkSession.live.done_by_user_and_date_range(
        user, from_date, to_date)
    for work_session in work_sessions:
      if work_session.hours:
        if work_session.project not in projects:
          projects[work_session.project] = WhatIDidPerProject(
              work_session.project, current_query_dict)
        projects[work_session.project].hours = round(
            projects[work_session.project].hours + work_session.hours, 2)
    all_user_to_dos = ProjectToDo.live.allowed_by_user(user).select_related(
        'project')
    to_dos = ProjectToDo.live.filter_done(
        all_user_to_dos, from_date, to_date)
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
