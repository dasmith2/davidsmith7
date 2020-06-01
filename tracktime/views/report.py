from django.shortcuts import render
from djaveLogin.login_required import login_required

from tracktime.views.util import (
    tracktime_context, PROJECT_WORK_SESSION_SUMMARY)
from tracktime.widgets.project_work_summary_table import (
    ProjectWorkSessionSummaryReport)
from tracktime.widgets.project_work_report import ProjectWorkReport


@login_required
def project_work_summary(request):
  report = ProjectWorkSessionSummaryReport(request.GET, request.user)
  context = tracktime_context(
      PROJECT_WORK_SESSION_SUMMARY, request, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)


@login_required
def project_work_report(request):
  report = ProjectWorkReport(request.GET, request.user)
  context = tracktime_context(
      PROJECT_WORK_SESSION_SUMMARY, request, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)
