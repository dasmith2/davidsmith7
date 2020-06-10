from django.db.models import Q
from django.shortcuts import reverse, render
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.problem import Problem
from djaveAPI.get_request_variable import (
    get_request_variable, get_obj_from_request_pk)
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.widgets.project_table import (
    ProjectTable, ArchivedProjectTable)
from tracktime.views.util import tracktime_context, PROJECTS


@login_required
def projects(request):
  context = projects_context(
      ProjectTable(request.user, request.POST), request,
      archived_projects_url=reverse('archived_projects'))
  return render(request, 'projects.html', context)


@login_required
def archived_projects(request):
  context = projects_context(ArchivedProjectTable(), request)
  return render(request, 'archived_projects.html', context)


def projects_context(table, request, **kwargs):
  context = tracktime_context(
      PROJECTS, request, table=table,
      archive_project_url=reverse('archive_project'),
      unarchive_project_url=reverse('unarchive_project'))
  context.update(kwargs)
  return context


@ajax_endpoint_login_required
def archive_project(request):
  get_obj_from_request_pk(request, Project).mark_deleted()


@ajax_endpoint_login_required
def unarchive_project(request):
  project = get_obj_from_request_pk(request, Project)
  project.deleted = None
  project.save()
