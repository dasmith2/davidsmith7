from datetime import date, timedelta
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse, redirect
from djAveJAX import ajax, AjaxProblem, get_ajax_variable, OK
from djaveNav.date_roller import DateRoller
from djaveURL import date_from_url

from tracktime.enter_time_table import EnterTimeTable
from tracktime.models.tracked import Tracked
from tracktime.punch_the_clock import PunchTheClockTable
from tracktime.views.util import tt_ui_context, ENTER_TIME


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
  enter_time_table = EnterTimeTable(user=request.user, day=day)
  if request.method == 'POST':
    if enter_time_table.form.save_button.key() in request.POST:
      enter_time_table = EnterTimeTable(
          user=request.user, day=day, form_data=request.POST)
      if enter_time_table.is_valid():
        enter_time_table.save()
        enter_time_table = EnterTimeTable(user=request.user, day=day)
  date_roller = DateRoller(ENTER_TIME, day, max_day=date.today())
  totals = Tracked.objects.total_hours_per_day(
      day - timedelta(days=2), day + timedelta(days=2), request.user)
  context = tt_ui_context(
      ENTER_TIME,
      delete_tracked_url=reverse('delete_tracked'),
      date_roller=date_roller,
      punch_the_clock_table=punch_the_clock_table,
      enter_time_table=enter_time_table,
      total_hours_per_day=json.dumps(totals))
  return render(request, 'enter_time.html', context)


@login_required
@ajax
def delete_tracked(request):
  pk = get_ajax_variable(request.POST, 'pk', required=True)
  tracked = Tracked.objects.filter(pk=pk).first()
  if not tracked:
    raise AjaxProblem('This Tracked does not exist')
  tracked.delete()
  return OK
