from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import reverse, render
from djAveJAX import ajax, get_ajax_variable, AjaxProblem

from tracktime.models.project import Project
from tracktime.tables.project_table import (
    ProjectTable, ArchivedProjectTable)
from tracktime.views.util import tracktime_context, PROJECTS


@login_required(login_url='/admin/login/')
def projects(request):
  context = projects_context(
      ProjectTable(request.POST),
      archived_projects_url=reverse('archived_projects'))
  return render(request, 'projects.html', context)


@login_required(login_url='/admin/login/')
def archived_projects(request):
  context = projects_context(ArchivedProjectTable())
  return render(request, 'archived_projects.html', context)


def projects_context(table, **kwargs):
  context = tracktime_context(
      PROJECTS, table=table,
      archive_project_url=reverse('archive_project'),
      unarchive_project_url=reverse('unarchive_project'),
      rename_project_url=reverse('rename_project'))
  context.update(kwargs)
  return context


@login_required
@ajax
def rename_project(request):
  project = get_ajax_project(request)
  name = get_ajax_variable(request.POST, 'name')
  if Project.all.filter(~Q(pk=project.pk), name=name).exists():
    raise AjaxProblem('A project with this name already exists')
  project.name = name
  project.save()


@login_required
@ajax
def archive_project(request):
  get_ajax_project(request).mark_deleted()


@login_required
@ajax
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
