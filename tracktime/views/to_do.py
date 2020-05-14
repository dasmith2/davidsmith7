from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect
from djaveDT import now
from djaveForm.button import Button
from djAveJAX import ajax, OK, AjaxProblem, get_ajax_variable
from djaveTable.problem import Problem

from tracktime.models.to_do import ToDo
from tracktime.models.tracked import Tracked
from tracktime.tables.punch_the_clock import PunchTheClockTable
from tracktime.tables.to_do_table import ToDoTable
from tracktime.views.util import tt_ui_context, TO_DO


@login_required(login_url='/admin/login/')
def to_do(request):
  # These have to go first because they might process a POST and change the
  # current project.
  punch_in_table = PunchTheClockTable(
      user=request.user, day=date.today(), show_abandoned=False,
      form_data=request.POST)
  punch_out_button = Button('Punch out', button_type='submit')

  project = None
  to_do_table = None
  clock_running = Tracked.live.get_clock_running(user=request.user)
  stop_problem = ''
  if clock_running:
    project = clock_running.project
    if request.method == 'POST' and punch_out_button.key() in request.POST:
      if clock_running.can_stop():
        clock_running.stop()
        return redirect('enter_time')
      stop_problem = Problem(clock_running.explain_why_can_not_stop())
    to_do_table = ToDoTable(
        user=request.user, project=project, form_data=request.POST)
  context = to_do_context(
      to_do_table, project=project,
      punch_in_table=punch_in_table,
      punch_out_button=punch_out_button,
      stop_problem=stop_problem,
      to_do_for_another_project_url=reverse('to_do_for_another_project'))
  return render(request, 'to_do.html', context)


@login_required
@ajax
def to_do_done(request):
  to_do = _ajax_to_do(request)
  to_do.done = now()
  to_do.save()
  return OK


@login_required
@ajax
def delete_to_do(request):
  _ajax_to_do(request).delete()
  return OK


@login_required
@ajax
def edit_description(request):
  to_do = _ajax_to_do(request)
  to_do.description = get_ajax_variable(request, 'description')
  to_do.save()
  return OK


def _ajax_to_do(request):
  pk = get_ajax_variable(request, 'pk')
  to_do = ToDo.live.filter(pk=pk).first()
  if not to_do:
    raise AjaxProblem('There is no ToDo with pk {}'.format(pk))
  return to_do


@login_required(login_url='/admin/login/')
def to_do_for_another_project(request):
  to_do_table = ToDoTable(
      user=request.user, project=None, form_data=request.POST)
  context = to_do_context(to_do_table)
  return render(request, 'to_do_for_another_project.html', context)


def to_do_context(to_do_table, **kwargs):
  return tt_ui_context(
      TO_DO, to_do_table=to_do_table,
      to_do_done_url=reverse(to_do_done),
      delete_to_do_url=reverse(delete_to_do),
      edit_description_url=reverse('edit_description'), **kwargs)
