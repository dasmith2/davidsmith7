from datetime import date

from django.shortcuts import render, reverse, redirect
from djaveDT import now
from djaveForm.button import Button
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.problem import Problem as AjaxProblem
from djaveAPI.get_request_variable import get_request_variable
from djaveLogin.login_required import login_required
from djaveTable.problem import Problem as HtmlProblem

from tracktime.models.to_do import ToDo
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.punch_the_clock import PunchTheClockTable
from tracktime.widgets.project_to_dos_table import ProjectToDosTable
from tracktime.widgets.all_project_to_dos import AllProjectToDos
from tracktime.views.util import tracktime_context, TO_DO


@login_required
def to_do(request):
  # These have to go first because they might process a POST and change the
  # current project.
  punch_in_table = PunchTheClockTable(
      user=request.user, day=date.today(), show_abandoned=False,
      form_data=request.POST)
  # key_prefix otherwise the punch out button in the punch_in_table takes over
  punch_out_button = Button(
      'Punch out', key_prefix='punch_out_on_to_do', button_type='submit')

  project = None
  to_dos_table = None
  clock_running = ProjectWorkSession.live.get_clock_running(user=request.user)
  stop_problem = ''
  if clock_running:
    project = clock_running.project
    if punch_out_button.get_was_clicked(request.POST):
      if clock_running.can_stop():
        clock_running.stop()
        return redirect('enter_time')
      stop_problem = HtmlProblem(clock_running.explain_why_can_not_stop())
    to_dos_table = ProjectToDosTable(
        user=request.user, form_data=request.POST, project=project)
    to_dos_table.populate_rows()
  context = to_do_context(
      to_dos_table, request, project=project,
      punch_in_table=punch_in_table,
      punch_out_button=punch_out_button,
      stop_problem=stop_problem,
      all_tasks_url=reverse('all_tasks'))
  return render(request, 'to_do.html', context)


@login_required
def all_tasks(request):
  all_project_to_dos = AllProjectToDos(request)
  context = to_do_context(all_project_to_dos, request)
  return render(request, 'all_tasks.html', context)


def to_do_context(to_dos_table, request, **kwargs):
  return tracktime_context(TO_DO, to_dos_table=to_dos_table, **kwargs)
