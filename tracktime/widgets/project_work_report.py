from datetime import timedelta

from django.shortcuts import reverse
from djaveDT import now
from djaveReport.date_range_report import DateRangeReport
from djaveURL import dict_as_query

from tracktime.fields import PROJECT, project_field
from tracktime.models.project import Project
from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)
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
    self.project = project
    super().__init__(user, from_date, to_date, tz_str=tz_str)

  def get_work_session_descriptions_object(self):
    return ProjectWorkSessionDescriptions(
        project=self.project,
        user=self.user,
        from_date=self.from_date,
        to_date=self.to_date,
        tz_str=self.tz_str)

  def html_header(self):
    if self.project:
      return '{}: {} hours'.format(self.project.name, self.get_total())
    return super().html_header()
