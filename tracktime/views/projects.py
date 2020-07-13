from django.shortcuts import reverse, render
from djaveLogin.login_required import login_required

from tracktime.widgets.projects_table import (
    ProjectsTable, ArchivedProjectsTable)
from tracktime.views.util import tracktime_context, PROJECTS


@login_required
def projects(request):
  context = projects_context(
      ProjectsTable(request.user, request.POST),
      archived_projects_url=reverse('archived_projects'))
  return render(request, 'projects.html', context)


@login_required
def archived_projects(request):
  context = projects_context(ArchivedProjectsTable(request.user))
  return render(request, 'archived_projects.html', context)


def projects_context(table, **kwargs):
  context = tracktime_context(PROJECTS, table=table)
  context.update(kwargs)
  return context
