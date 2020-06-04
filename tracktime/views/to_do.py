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
from tracktime.widgets.project_to_do_table import ProjectToDoTable
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
  to_do_table = None
  clock_running = ProjectWorkSession.live.get_clock_running(user=request.user)
  stop_problem = ''
  if clock_running:
    project = clock_running.project
    if punch_out_button.get_was_clicked(request.POST):
      if clock_running.can_stop():
        clock_running.stop()
        return redirect('enter_time')
      stop_problem = HtmlProblem(clock_running.explain_why_can_not_stop())
    to_do_table = ProjectToDoTable(
        user=request.user, project=project, form_data=request.POST)
  context = to_do_context(
      to_do_table, request, project=project,
      punch_in_table=punch_in_table,
      punch_out_button=punch_out_button,
      stop_problem=stop_problem,
      to_do_for_another_project_url=reverse('to_do_for_another_project'))
  return render(request, 'to_do.html', context)


@ajax_endpoint_login_required
def to_do_done(request):
  to_do = _ajax_to_do(request)
  to_do.done = now()
  to_do.done_by = request.user
  to_do.save()


@ajax_endpoint_login_required
def to_do_not_done(request):
  to_do = _ajax_to_do(request)
  to_do.done = None
  to_do.done_by = None
  to_do.save()


@ajax_endpoint_login_required
def delete_to_do(request):
  _ajax_to_do(request).mark_deleted()


@ajax_endpoint_login_required
def edit_description(request):
  to_do = _ajax_to_do(request)
  to_do.description = get_request_variable(request, 'description')
  to_do.save()


def _ajax_to_do(request):
  pk = get_request_variable(request, 'pk')
  to_do = ToDo.live.filter(pk=pk).first()
  if not to_do:
    raise AjaxProblem('There is no ToDo with pk {}'.format(pk))
  return to_do


@login_required
def to_do_for_another_project(request):
  to_do_table = ProjectToDoTable(
      user=request.user, project=None, form_data=request.POST)
  context = to_do_context(to_do_table, request)
  return render(request, 'to_do_for_another_project.html', context)


def to_do_context(to_do_table, request, **kwargs):
  return tracktime_context(
      TO_DO, request, to_do_table=to_do_table,
      to_do_done_url=reverse(to_do_done),
      not_done_url=reverse(to_do_not_done),
      delete_to_do_url=reverse(delete_to_do),
      edit_description_url=reverse('edit_description'), **kwargs)
