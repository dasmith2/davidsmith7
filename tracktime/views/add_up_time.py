from django.contrib.auth.decorators import login_required



@login_required(login_url='/admin/login/')
def add_up_time(request):
  filters = AddUpTimeFiltersTable()
  filters.set_form_data(request.GET)
  context = tt_ui_context(ADD_UP_TIME, filters=filters)
  return render(request, 'add_up_time.html', context)
