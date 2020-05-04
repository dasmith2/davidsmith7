from django.contrib.auth.decorators import login_required

from tracktime.views.util import tt_ui_context



@login_required(login_url='/admin/login/')
def to_do(request):
  project = Tracked.objects.currently_tracking_project()
  context = tt_ui_context(
      TO_DO, project=project, punch_the_clock_table=None, to_dos=None)
  if project:
    context['to_dos'] = ToDo.objects.not_checked_off(request.user, project)
  else:
    context['punch_the_clock_table'] = PunchTheClockTable(
        user=request.user, day=date.today(), form_data=request.POST)
  return render(request, 'to_do.html', context)
