from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from djavError.log_error import log_error
from djavError.models.error import Error
from djavError.nav_context import (
    nav_context, ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES,
    TRIGGER_ERRORS)
from djavError.widgets.errors_report import ErrorsReport
from djavError.widgets.notifications_report import NotificationsReport
from djavError.widgets.trigger_errors import TriggerErrors


@user_passes_test(lambda u: u.is_superuser)
def errors(request):
  context = nav_context(
      ERRORS, the_one_thing_on_the_page=ErrorsReport(request.GET))
  return render(request, 'error_base.html', context)


@user_passes_test(lambda u: u.is_superuser)
def notifications(request):
  context = nav_context(
      NOTIFICATIONS,
      the_one_thing_on_the_page=NotificationsReport(request.GET))
  return render(request, 'error_base.html', context)


@user_passes_test(lambda u: u.is_superuser)
def trigger_errors(request):
  context = nav_context(
      TRIGGER_ERRORS,
      the_one_thing_on_the_page=TriggerErrors(request, request.POST))
  return render(request, 'error_base.html', context)


@csrf_exempt
def js_error(request):
  post = request.POST
  message = (
      'This is a Javascript error caught by '
      'main/templates/js/error.js\n\nuser: {}\n\n{} line {} column {}'
      '\nReferer {}\nStack {}').format(
          request.user, post.get('url', ''),
          post.get('line', ''), post.get('col', ''),
          request.META.get('HTTP_REFERER', ''), post.get('stack', ''))
  subject = post.get('msg', 'Javascript error received')
  log_error(subject, message, supress_stack_trace=True)
  return HttpResponse('ok')


@user_passes_test(lambda u: u.is_superuser)
def long_requests(request):
  context = nav_context(LONG_REQUESTS)
  return render(request, 'error_base.html', context)


@user_passes_test(lambda u: u.is_superuser)
def too_many_queries(request):
  context = nav_context(TOO_MANY_QUERIES)
  return render(request, 'error_base.html', context)


@user_passes_test(lambda u: u.is_superuser)
def see_error(request, pk):
  error = Error.objects.get(pk=pk)
  parts = [
      error.title,
      error.message,
      error.error_message,
      error.stack_trace]
  return HttpResponse(
      '\n'.join(['<pre>{}</pre>'.format(part) for part in parts]))
