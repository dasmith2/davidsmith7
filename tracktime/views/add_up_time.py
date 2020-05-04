from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tracktime.add_up_time_filters_table import AddUpTimeFiltersTable
from tracktime.views.util import ADD_UP_TIME, tt_ui_context


@login_required(login_url='/admin/login/')
def add_up_time(request):
  filters = AddUpTimeFiltersTable()
  filters.set_form_data(request.GET)
  context = tt_ui_context(ADD_UP_TIME, filters=filters)
  return render(request, 'add_up_time.html', context)
