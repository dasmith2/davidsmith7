from django.shortcuts import reverse, render, get_object_or_404, redirect
from djaveHTML.form_wrapper import FormWrapper
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.views.nav_context import tracktime_context, PROJECTS
from tracktime.widgets.project_table import ProjectTable
from tracktime.widgets.projects import Projects, ArchivedProjects


@login_required
def projects(request):
  archived_projects_exist = Project.allowed_by_user(request.user).filter(
      deleted__isnull=False).exists()
  context = projects_context(
      request.user, table=Projects(),
      archived_projects_url=reverse('archived_projects'),
      archived_projects_exist=archived_projects_exist)
  return render(request, 'projects.html', context)


@login_required
def archived_projects(request):
  context = projects_context(request.user, table=ArchivedProjects())
  return render(request, 'archived_projects.html', context)


@login_required
def edit_project(request, pk=None):
  project = None
  title = 'New Project'
  if pk:
    project = get_object_or_404(Project.allowed_by_user(request.user), pk=pk)
    title = project.name

  table = ProjectTable(request.user, request.POST, project)
  if table.saved() or table.deleted():
    return redirect('projects')

  form_wrapper = FormWrapper(table, request)
  context = projects_context(
      request.user, the_one_thing_on_the_page=form_wrapper, title=title)
  return render(request, 'tracktime_base.html', context)


def projects_context(user, **kwargs):
  return tracktime_context(user, PROJECTS, **kwargs)
