from datetime import date, timedelta
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect
from djAveJAX import ajax, AjaxProblem, get_ajax_variable, OK
from djaveNav.date_roller import DateRoller
from djaveURL import date_from_url

from tracktime.models.work_session import WorkSession
from tracktime.tables.enter_time_table import EnterTimeTable
from tracktime.tables.punch_the_clock import PunchTheClockTable
from tracktime.views.util import tracktime_context, ENTER_TIME


@login_required(login_url='/admin/login/')
def enter_time(request):
  day = date_from_url(request)
  punch_the_clock_table = None
  punch_the_clock_table = PunchTheClockTable(
      user=request.user, day=day, form_data=request.POST)
  if punch_the_clock_table.started_clock_on_project:
    return redirect('to_do')
  if day != date.today():
    punch_the_clock_table = None
  enter_time_table = EnterTimeTable(
      user=request.user, day=day, form_data=request.POST)
  date_roller = DateRoller(ENTER_TIME, day, max_day=date.today())
  totals = WorkSession.live.total_hours_per_date(
      day - timedelta(days=2), day + timedelta(days=2), request.user)
  context = tracktime_context(
      ENTER_TIME,
      delete_work_session_url=reverse('delete_work_session'),
      date_roller=date_roller,
      punch_the_clock_table=punch_the_clock_table,
      enter_time_table=enter_time_table,
      total_hours_per_date=json.dumps(totals))
  return render(request, 'enter_time.html', context)


@login_required
@ajax
def delete_work_session(request):
  pk = get_ajax_variable(request.POST, 'pk', required=True)
  work_session = WorkSession.live.filter(pk=pk).first()
  if not work_session:
    raise AjaxProblem('This WorkSession does not exist')
  work_session.mark_deleted()
  return OK
