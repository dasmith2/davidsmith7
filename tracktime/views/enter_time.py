from datetime import date, timedelta
import json

from django.shortcuts import render, reverse, redirect
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.problem import Problem
from djaveLogin.login_required import login_required
from djaveNav.date_roller import DateRoller
from djaveURL import date_from_url

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.enter_time_table import EnterTimeTable
from tracktime.widgets.punch_the_clock import PunchTheClockTable
from tracktime.views.util import tracktime_context, ENTER_TIME


@login_required
def enter_time(request):
  day = date_from_url(request)
  punch_the_clock_table = None
  punch_the_clock_table = PunchTheClockTable(
      user=request.user, day=day, form_data=request.POST)
  projects_exist = punch_the_clock_table.has_projects
  if punch_the_clock_table.started_clock_on_project:
    return redirect('to_do')
  if day != date.today():
    punch_the_clock_table = None
  enter_time_table = EnterTimeTable(
      user=request.user, day=day, form_data=request.POST)
  date_roller = DateRoller(ENTER_TIME, day, max_day=date.today())
  totals = ProjectWorkSession.live.total_hours_per_date(
      day - timedelta(days=2), day + timedelta(days=2), request.user)
  context = tracktime_context(
      ENTER_TIME,
      delete_work_session_url=reverse('delete_work_session'),
      date_roller=date_roller,
      punch_the_clock_table=punch_the_clock_table,
      enter_time_table=enter_time_table,
      total_hours_per_date=json.dumps(totals),
      projects_exist=projects_exist)
  return render(request, 'enter_time.html', context)


@ajax_endpoint_login_required
def delete_work_session(request):
  pk = get_request_variable(request.POST, 'pk', required=True)
  work_session = ProjectWorkSession.live.filter(pk=pk).first()
  if not work_session:
    raise Problem('This ProjectWorkSession does not exist')
  work_session.mark_deleted()
