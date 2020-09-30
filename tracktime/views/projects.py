from django.shortcuts import reverse, render
from djaveHTML.a import A
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.views.nav_context import tracktime_context, PROJECTS
from tracktime.widgets.projects import Projects, ArchivedProjects


@login_required
def projects(request):
  archived_projects_link = A(
      'See archived projects', reverse('archived_projects'),
      css_classes=['archived-projects-link'])
  archived_projects_exist = Project.allowed_by_user(request.user).filter(
      deleted__isnull=False).exists()
  if not archived_projects_exist:
    archived_projects_link.add_css_class('start-hidden')
  context = projects_context(
      request.user, table=Projects(),
      archived_projects_link=archived_projects_link)
  return render(request, 'projects.html', context)


@login_required
def archived_projects(request):
  context = projects_context(request.user, table=ArchivedProjects())
  return render(request, 'archived_projects.html', context)


def projects_context(user, **kwargs):
  return tracktime_context(user, PROJECTS, **kwargs)
