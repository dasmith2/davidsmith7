from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tracktime.views.util import tt_ui_context, REPORT
from tracktime.tables.what_i_did_report import WhatIDidReport
from tracktime.tables.time_breakdown import TimeBreakdown


@login_required(login_url='/admin/login/')
def report(request):
  report = WhatIDidReport(request.GET, request.user)
  context = tt_ui_context(REPORT, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)


def time_breakdown(request):
  report = TimeBreakdown(request.GET, request.user)
  context = tt_ui_context(REPORT, the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)
