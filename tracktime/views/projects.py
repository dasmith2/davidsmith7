from django.db.models import Q
from django.shortcuts import reverse, render
from djAveJAX import ajax_login_required, get_ajax_variable, AjaxProblem
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.tables.project_table import (
    ProjectTable, ArchivedProjectTable)
from tracktime.views.util import tracktime_context, PROJECTS


@login_required
def projects(request):
  context = projects_context(
      ProjectTable(request.POST), request,
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
      unarchive_project_url=reverse('unarchive_project'),
      rename_project_url=reverse('rename_project'))
  context.update(kwargs)
  return context


@ajax_login_required
def rename_project(request):
  project = get_ajax_project(request)
  name = get_ajax_variable(request.POST, 'name')
  if Project.all.filter(~Q(pk=project.pk), name=name).exists():
    raise AjaxProblem('A project with this name already exists')
  project.name = name
  project.save()


@ajax_login_required
def archive_project(request):
  get_ajax_project(request).mark_deleted()


@ajax_login_required
def unarchive_project(request):
  project = get_ajax_project(request)
  project.deleted = None
  project.save()


def get_ajax_project(request):
  pk = get_ajax_variable(request.POST, 'pk')
  project = Project.all.filter(pk=pk).first()
  if not project:
    raise AjaxProblem('This project does not exist')
  return project
