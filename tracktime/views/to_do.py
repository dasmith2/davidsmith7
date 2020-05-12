from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect
from djaveDT import now
from djaveForm.button import Button
from djAveJAX import ajax, OK, AjaxProblem, get_ajax_variable

from tracktime.models.to_do import ToDo
from tracktime.models.tracked import Tracked
from tracktime.views.util import tt_ui_context, TO_DO
from tracktime.punch_the_clock import PunchTheClockTable
from tracktime.to_do_table import ToDoTable


@login_required(login_url='/admin/login/')
def to_do(request):
  # These have to go first because they might process a POST and change the
  # current project.
  punch_the_clock_table = PunchTheClockTable(
      user=request.user, day=date.today(), form_data=request.POST)
  punch_out_button = Button('Punch out', button_type='submit')

  project = None
  to_do_table = None
  can_punch_out = Tracked.objects.get_can_punch_out(user=request.user)
  if can_punch_out:
    project = can_punch_out.project
    if request.method == 'POST' and punch_out_button.key() in request.POST:
      can_punch_out.stop()
      return redirect('enter_time')
    else:
      to_do_table = ToDoTable(
          user=request.user, project=project, form_data=request.POST)
  context = tt_ui_context(
      TO_DO, project=project, punch_the_clock_table=punch_the_clock_table,
      to_do_table=to_do_table, to_do_done_url=reverse(to_do_done),
      delete_to_do_url=reverse(delete_to_do),
      punch_out_button=punch_out_button)
  return render(request, 'to_do.html', context)


@login_required
@ajax
def to_do_done(request):
  to_do = _ajax_to_do(request)
  to_do.checked_off = now()
  to_do.save()
  return OK


@login_required
@ajax
def delete_to_do(request):
  _ajax_to_do(request).delete()
  return OK


def _ajax_to_do(request):
  pk = get_ajax_variable(request, 'pk')
  to_do = ToDo.objects.filter(pk=pk).first()
  if not to_do:
    raise AjaxProblem('There is no ToDo with pk {}'.format(pk))
  return to_do
