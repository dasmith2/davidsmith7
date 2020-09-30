from django.shortcuts import render
from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.paged_results import construct_paged_results
from djaveDT import parse_dt
from djaveHTML.a import A
from djaveLogin.login_required import login_required

from tracktime.views.nav_context import (
    tracktime_context, PROJECT_WORK_SESSION_SUMMARY)
from tracktime.widgets.project_work_summary import (
    ProjectWorkSummary, get_what_i_did_per_projects)
from tracktime.widgets.project_work_report import ProjectWorkReport


@login_required
def project_work_summary(request):
  context = tracktime_context(
      request.user, PROJECT_WORK_SESSION_SUMMARY,
      the_one_thing_on_the_page=ProjectWorkSummary(request.user))
  return render(request, 'tracktime_base.html', context)


@login_required
def project_work_report(request):
  report = ProjectWorkReport(request.GET, request.user)
  context = tracktime_context(
      request.user, PROJECT_WORK_SESSION_SUMMARY,
      the_one_thing_on_the_page=report)
  return render(request, 'tracktime_base.html', context)


@ajax_or_api_endpoint_authenticated
def project_work_summary_data(request_method, request_dict, credentials):
  user = credentials.user
  work_from = parse_dt(get_request_variable(request_dict, 'work_from__gte'))
  work_to = parse_dt(get_request_variable(request_dict, 'work_from__lte'))

  results = []
  for what_i_did_per_project in get_what_i_did_per_projects(
      user, work_from, work_to, request_dict):
    hours = A(
        what_i_did_per_project.hours, what_i_did_per_project.breakdown_url)
    results.append({
        'project': what_i_did_per_project.project.name,
        'hours': hours.as_html(), 'done': what_i_did_per_project.done})
  return construct_paged_results(results)
