import hashlib

from django.conf import settings
from django.shortcuts import render
from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.get_instance import get_instance
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.paged_results import construct_paged_results
from djaveDT import parse_dt
from djaveHTML.a import A
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.models.project_work_session_description import (
    ProjectWorkSessionDescriptions)
from tracktime.views.nav_context import (
    tracktime_context, PROJECT_WORK_SESSION_SUMMARY)
from tracktime.widgets.project_work_sessions import ProjectWorkSessions
from tracktime.widgets.project_work_summary import (
    ProjectWorkSummary, get_what_i_did_per_projects)


@login_required
def project_work_summary(request):
  context = tracktime_context(
      request.user, PROJECT_WORK_SESSION_SUMMARY,
      the_one_thing_on_the_page=ProjectWorkSummary(request.user))
  return render(request, 'tracktime_base.html', context)


@login_required
def project_work_report(request):
  context = tracktime_context(
      request.user, PROJECT_WORK_SESSION_SUMMARY,
      the_one_thing_on_the_page=ProjectWorkSessions(request.user))
  return render(request, 'project_work_report.html', context)


@ajax_or_api_endpoint_authenticated
def project_work_summary_data(request_method, request_dict, credentials):
  user = credentials.user
  work_from = parse_dt(get_request_variable(request_dict, 'work_from__gte'))
  work_to = parse_dt(get_request_variable(request_dict, 'work_from__lte'))

  results = []
  for per_project in get_what_i_did_per_projects(
      user, work_from, work_to, request_dict):
    project_name = A(per_project.project.name, per_project.breakdown_url)
    results.append({
        'project': project_name.as_html(), 'id': per_project.project.pk,
        'hours': per_project.hours, 'done': per_project.done})
  return construct_paged_results(results)


@ajax_or_api_endpoint_authenticated
def project_work_session_description_data(
    request_method, request_dict, credentials):
  user = credentials.user
  work_from = parse_dt(get_request_variable(request_dict, 'work_from__gte'))
  work_to = parse_dt(get_request_variable(request_dict, 'work_from__lte'))
  project = None
  project_id = get_request_variable(request_dict, 'project', required=False)
  if project_id:
    project = get_instance(Project.live, project_id, credentials)

  results = []

  descriptions = ProjectWorkSessionDescriptions(
      project=project, user=user, from_dt=work_from, to=work_to,
      tz_str=settings.TIME_ZONE)

  def describe(id, css_class, description, hours):
    return {
        'id': id, 'css_class': css_class, 'description': description,
        'hours': hours}

  for work_session in descriptions.get_work_session_descriptions():
    results.append(describe(
        'ws_{}'.format(work_session.work_session.pk),
        'work-session slightly-bigger-font', work_session.time_description,
        work_session.hours))
    for to_do_description in work_session.to_do_descriptions:
      to_do_id = hashlib.md5(str.encode(to_do_description)).hexdigest()[:7]
      results.append(describe(to_do_id, 'to-do', to_do_description, 0))

  return construct_paged_results(results)
