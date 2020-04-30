from collections import namedtuple
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from djaveDT import days_ago_str
from djAveJAX import ajax, AjaxProblem, get_ajax_variable, OK
from djaveNav.nav import NavItem, Nav
from djaveNav.date_roller import DateRoller
from djaveURL import url_with_date, date_from_url
from tracktime.add_up_time_filters_table import AddUpTimeFiltersTable
from tracktime.enter_time_table import EnterTimeTable
from tracktime.models import Tracked
from tracktime.punch_the_clock import PunchTheClockTable


ENTER_TIME = 'enter_time'
ADD_UP_TIME = 'add_up_time'
NAV_LIST = [
    NavItem(ENTER_TIME, 'Enter time'),
    NavItem(ADD_UP_TIME, 'Add up time')]


def tt_ui_context(current_view, **kwargs):
  context = {'nav': Nav(NAV_LIST, current_view)}
  context.update(kwargs)
  return context


@login_required(login_url='/admin/login/')
def enter_time(request):
  day = date_from_url(request)
  punch_the_clock_table = None
  punch_the_clock_table = PunchTheClockTable(
      user=request.user, day=day, form_data=request.POST)
  enter_time_table = EnterTimeTable(user=request.user, day=day)
  if request.method == 'POST':
    if enter_time_table.form.save_button.key() in request.POST:
      enter_time_table = EnterTimeTable(
          user=request.user, day=day, form_data=request.POST)
      if enter_time_table.is_valid():
        tracked = enter_time_table.save()
        enter_time_table = EnterTimeTable(user=request.user, day=day)
  date_roller = DateRoller(ENTER_TIME, day, max_day=date.today())
  context = tt_ui_context(
      ENTER_TIME,
      delete_tracked_url=reverse('delete_tracked'),
      date_roller=date_roller,
      punch_the_clock_table=punch_the_clock_table,
      enter_time_table=enter_time_table)
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


@login_required(login_url='/admin/login/')
def add_up_time(request):
  filters = AddUpTimeFiltersTable()
  filters.set_form_data(request.GET)
  context = tt_ui_context(ADD_UP_TIME, filters=filters)
  return render(request, 'add_up_time.html', context)


@login_required(login_url='/admin/login/')
def time_list(request):
  context = tt_ui_context(ADD_UP_TIME)
  return render(request, 'time_list.html', context)
