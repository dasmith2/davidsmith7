from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from djavError.views.util import error_context, NOTIFICATIONS
from djavError.widgets.notifications_report import NotificationsReport


@user_passes_test(lambda u: u.is_superuser)
def notifications(request):
  context = error_context(
      NOTIFICATIONS,
      the_one_thing_on_the_page=NotificationsReport(request.GET))
  return render(request, 'error_base.html', context)
