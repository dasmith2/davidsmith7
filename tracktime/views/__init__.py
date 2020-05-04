from collections import namedtuple
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse

from djaveDT import days_ago_str
from djAveJAX import ajax, AjaxProblem, get_ajax_variable, OK
from djaveNav.date_roller import DateRoller
from djaveURL import date_from_url
from tracktime.add_up_time_filters_table import AddUpTimeFiltersTable
from tracktime.enter_time_table import EnterTimeTable
from tracktime.models import Tracked
from tracktime.punch_the_clock import PunchTheClockTable

from tracktime.views.enter_time import enter_time, delete_tracked
from tracktime.views.add_up_time import add_up_time
from tracktime.views.to_do import to_do
