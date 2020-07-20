from datetime import date

from django.shortcuts import render, reverse, redirect, get_object_or_404
from djaveForm.button import Button
from djaveLogin.login_required import login_required
from djaveTable.cell_content import InHref
from djaveTable.problem import Problem as HtmlProblem

from tracktime.models.project import Project
from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.punch_the_clock import PunchTheClockTable
from tracktime.widgets.project_to_dos_table import ProjectToDosTable
from tracktime.widgets.all_project_to_dos import AllProjectToDos
from tracktime.views.util import tracktime_context, TO_DO


@login_required
def to_do(request, project_pk=None):
  # These have to go first because they might process a POST and change the
  # current project.
  punch_in_table = PunchTheClockTable(
      user=request.user, day=date.today(), show_abandoned=False,
      form_data=request.POST, see_all_tasks_button=True,
      only_show_has_to_do_list=True)
  # key_prefix otherwise the punch out button in the punch_in_table takes over
  punch_out_button = Button(
      'Punch out', key_prefix='punch_out_on_to_do', button_type='submit')

  project = None
  to_dos_table = None
  clock_running = ProjectWorkSession.live.get_clock_running(user=request.user)
  stop_problem = ''
  if project_pk:
    project = get_object_or_404(
        Project.allowed_by_user_live(request.user), pk=project_pk)
  if clock_running:
    project = clock_running.project
    if punch_out_button.get_was_clicked(request.POST):
      if clock_running.can_stop():
        clock_running.stop()
        return redirect('enter_time')
      stop_problem = HtmlProblem(clock_running.explain_why_can_not_stop())
  use_clock = False
  see_all_tasks = InHref('See ALL tasks', reverse('all_tasks'))
  if project and project.has_to_do_list:
    to_dos_table = ProjectToDosTable(
        user=request.user, form_data=request.POST, project=project)
    to_dos_table.populate_rows()
    use_clock = project.use_clock
  context = to_do_context(
      to_dos_table, request, project=project,
      punch_in_table=punch_in_table,
      punch_out_button=punch_out_button,
      use_clock=use_clock,
      stop_problem=stop_problem,
      see_all_tasks=see_all_tasks)
  return render(request, 'to_do.html', context)


@login_required
def all_tasks(request):
  all_project_to_dos = AllProjectToDos(request)
  context = to_do_context(all_project_to_dos, request)
  return render(request, 'all_tasks.html', context)


def to_do_context(to_dos_table, request, **kwargs):
  return tracktime_context(TO_DO, to_dos_table=to_dos_table, **kwargs)
