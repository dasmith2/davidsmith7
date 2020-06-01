from datetime import timedelta

from django.shortcuts import reverse
from djaveDT import now
from djaveTable.cell_content import InHref
from djaveTable.table import Table
from djaveReport.date_range_report import DateRangeReport
from djaveURL import dict_as_query

from tracktime.models.project_work_session import ProjectWorkSession


class WhatIDidReport(DateRangeReport):
  def __init__(self, request_get, user, nnow=None):
    nnow = nnow or now()
    default_from_date = nnow.date() - timedelta(days=7)
    default_to_date = nnow.date()
    super().__init__(default_from_date, default_to_date, request_get)

    current_query_dict = self.get_query_dict()
    self.what_i_did_content = WhatIDidReportContent(
        user, self.from_date(), self.to_date(), current_query_dict)
    self.add_content(self.what_i_did_content)


class WhatIDidReportContent(Table):
  def __init__(self, user, from_date, to_date, current_query_dict):
    super().__init__(['Project', 'Hours'])

    self.projects = self.get_projects(
        user, from_date, to_date, current_query_dict)
    for project in self.projects:
      self.create_row([
          project.name,
          InHref(project.hours, project.hours_breakdown_url)])

  def get_projects(self, user, from_date, to_date, current_query_dict):
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
    return sorted(list(projects.values()), key=lambda x: x.name)


class WhatIDidPerProject(object):
  def __init__(self, project, current_query_dict):
    self.name = project.name
    self.hours = 0.0
    # This is why the WhatIDidPerProject filters should be exactly the same as
    # the WorkReport filters, except time breakdown is also by project.
    use_query_dict = {'project': project.pk}
    use_query_dict.update(current_query_dict)
    self.hours_breakdown_url = reverse(
        'project_work_report') + dict_as_query(use_query_dict)
