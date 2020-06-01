from django.shortcuts import render
from djaveLogin.login_required import login_required

from tracktime.views.util import tracktime_context, REPORT
from tracktime.widgets.what_i_did_report import WhatIDidReport
from tracktime.widgets.project_work_report import ProjectWorkReport


@login_required
def report(request):
  report = WhatIDidReport(request.GET, request.user)
  context = tracktime_context(
      REPORT, request, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)


@login_required
def project_work_report(request):
  report = ProjectWorkReport(request.GET, request.user)
  context = tracktime_context(
      REPORT, request, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)
