from datetime import timedelta

from django.shortcuts import reverse
from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from djaveURL import dict_as_query

from tracktime.fields import PROJECT, project_field
from tracktime.models.project import Project
from tracktime.models.project_to_do import ProjectToDo
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.work_report import (
    WorkReportContent, work_report_url_dict)


def project_work_report_url(project, from_date=None, to_date=None):
  query_dict = work_report_url_dict(from_date=from_date, to_date=to_date)
  query_dict[PROJECT] = project.pk
  return '{}{}'.format(
      reverse('project_work_report'), dict_as_query(query_dict))


class ProjectWorkReport(DateRangeReport):
  def __init__(self, request_get, user, nnow=None):
    nnow = nnow or now()
    default_from_date = nnow.date() - timedelta(days=7)
    default_to_date = nnow.date()
    project_select = project_field(label='Project')
    super().__init__(
        default_from_date, default_to_date, request_get,
        filters=[project_select])

    project = None
    if PROJECT in request_get:
      project = Project.live.filter(pk=request_get[PROJECT]).first()

    self.work_report_content = ProjectWorkReportContent(
        user, project, self.from_date(), self.to_date())
    self.add_content(self.work_report_content)


class ProjectWorkReportContent(WorkReportContent):
  def __init__(self, user, project, from_date, to_date, tz_str=None):
    super().__init__(user, from_date, to_date, tz_str=tz_str)
    self.project = project

  def show_project(self):
     return not self.project

  def work_session_class(self):
    return ProjectWorkSession

  def to_do_class(self):
    return ProjectToDo

  def get_work_sessions(self):
    work_sessions = super().get_work_sessions()
    if self.project:
      work_sessions = list(filter(
          lambda x: x.project == self.project, work_sessions))
    return work_sessions

  def get_to_dos(self):
    to_dos = super().get_to_dos()
    if self.project:
      to_dos = list(filter(lambda x: x.project == self.project, to_dos))
    return to_dos

  def time_description(self, work_session):
    description = super().time_description(work_session)
    if self.show_project():
      description = '{} {}'.format(work_session.project.name, description)
    return description

  def to_do_description(self, to_do):
    description = super().to_do_description(to_do)
    if self.show_project():
      description = '{} {}'.format(to_do.project.name, description)
    return description

  def html_header(self):
    total = round(self.total, 2)
    if self.project:
      return '{}: {} hours'.format(self.project.name, total)
    return super().html_header()
