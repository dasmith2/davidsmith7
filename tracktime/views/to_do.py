from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render, reverse, redirect, get_object_or_404

from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.filters import filter_model
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.views.api import (
    do_list_or_save_new, do_get_save_or_delete_existing)
from djaveDT import now
from djaveHTML.button import Button
from djaveHTML.a import A
from djaveHTML.problem import Problem as HtmlProblem
from djaveLogin.login_required import login_required

from tracktime.models.project import Project
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.to_do_project_picker import ToDoProjectPicker
from tracktime.widgets.project_to_dos import ProjectToDos, AllProjectToDos
from tracktime.views.nav_context import tracktime_context, TO_DO


@login_required
def to_dos(request, project_pk=None):
  to_do_project_picker = ToDoProjectPicker(request.user, request.POST)
  punch_out_button = Button('Punch out', button_type='submit')

  to_dos_table = None
  clock_running = ProjectWorkSession.live.get_clock_running(user=request.user)
  stop_problem = ''

  project = None
  list_url = reverse('to_dos')
  if project_pk:
    project = get_object_or_404(
        Project.allowed_by_user_live(request.user), pk=project_pk)
    list_url = reverse('to_dos', kwargs={'project_pk': project_pk})

  if clock_running:
    project = clock_running.project
    if punch_out_button.get_was_clicked(request.POST):
      if clock_running.can_stop():
        clock_running.stop()
        return redirect('enter_time')
      stop_problem = HtmlProblem(clock_running.explain_why_can_not_stop())
  use_clock = False
  see_all_tasks = A(
      'See ALL tasks', reverse('all_to_dos'), css_classes=['all_to_dos'])
  if project and project.has_to_do_list:
    to_dos_table = ProjectToDos(project, list_url)
    use_clock = project.use_clock
  context = to_do_context(
      to_dos_table, request, project=project,
      to_do_project_picker=to_do_project_picker,
      punch_out_button=punch_out_button,
      use_clock=use_clock,
      stop_problem=stop_problem,
      see_all_tasks=see_all_tasks)
  return render(request, 'to_do.html', context)


@login_required
def all_to_dos(request):
  all_project_to_dos = AllProjectToDos(request.user)
  context = tracktime_context(
      request.user, TO_DO, the_one_thing_on_the_page=all_project_to_dos)
  return render(request, 'tracktime_base.html', context)


def to_do_context(to_dos_table, request, **kwargs):
  return tracktime_context(
      request.user, TO_DO, to_dos_table=to_dos_table, **kwargs)


MODEL_NAME = 'ProjectToDo'


@ajax_or_api_endpoint_authenticated
def project_to_dos_for_ui(request_method, request_dict, credentials):
  if request_method == 'GET':
    recent = request_dict.pop('recent', False)
    filtered = filter_model(MODEL_NAME, credentials, request_dict).filter(
        project__deleted__isnull=True).order_by('sort_timestamp', 'pk')
    if recent:
      filtered = filtered.filter(
          Q(done__gte=now() - timedelta(days=1)) | Q(done__isnull=True))
    return paged_results(filtered, page=get_page(request_dict))
  return do_list_or_save_new(
      request_method, request_dict, credentials, MODEL_NAME)


@ajax_or_api_endpoint_authenticated
def project_to_do_for_ui(
    request_method, request_dict, credentials, pk):
  return do_get_save_or_delete_existing(
      request_method, request_dict, credentials, MODEL_NAME, pk)
