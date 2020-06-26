from django.shortcuts import reverse, render
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_request_ajax_obj
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.widgets.projects_table import (
    ProjectsTable, ArchivedProjectsTable)
from tracktime.views.util import tracktime_context, PROJECTS


@login_required
def projects(request):
  context = projects_context(
      ProjectsTable(request.user, request.POST), request,
      archived_projects_url=reverse('archived_projects'))
  return render(request, 'projects.html', context)


@login_required
def archived_projects(request):
  context = projects_context(ArchivedProjectsTable(request.user), request)
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
  get_request_ajax_obj(request, Project).mark_deleted()


@ajax_endpoint_login_required
def unarchive_project(request):
  project = get_request_ajax_obj(request, Project)
  project.deleted = None
  project.save()
