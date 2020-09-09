from datetime import date, timedelta
import json

from django.shortcuts import render, redirect
from djaveLogin.login_required import login_required
from djaveNav.date_roller import DateRoller
from djaveURL import date_from_url

from tracktime.models.project_work_session import ProjectWorkSession
from tracktime.widgets.enter_time_table import EnterTimeTable2
from tracktime.widgets.punch_the_clock import PunchTheClock
from tracktime.views.nav_context import tracktime_context, ENTER_TIME


@login_required
def enter_time(request):
  day = date_from_url(request)
  punch_the_clock = PunchTheClock(
      user=request.user, day=day, form_data=request.POST)
  if punch_the_clock.started_project and (
      punch_the_clock.started_project.has_to_do_list):
    return redirect('to_dos')

  projects_exist = punch_the_clock.has_projects
  if day != date.today():
    punch_the_clock = None

  enter_time_table = EnterTimeTable2(request.user, day)
  date_roller = DateRoller(ENTER_TIME, day, max_day=date.today())
  totals = ProjectWorkSession.live.total_hours_per_date(
      day - timedelta(days=2), day + timedelta(days=2), request.user)
  context = tracktime_context(
      request.user, ENTER_TIME,
      date_roller=date_roller,
      punch_the_clock=punch_the_clock,
      enter_time_table=enter_time_table,
      total_hours_per_date=json.dumps(totals),
      projects_exist=projects_exist)
  return render(request, 'enter_time.html', context)
