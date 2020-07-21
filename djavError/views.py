from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from djaveAPI.ajax_endpoint import ajax_endpoint
from djaveClassMagic.find_models import model_from_name
from djaveDT import now
from djavError.log_error import log_error
from djavError.models.error import Error
from djavError.models.fixable import Fixable
from djavError.nav_context import (
    nav_context, ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES,
    TRIGGER_ERRORS)
from djavError.widgets.errors_report import ErrorsReport
from djavError.widgets.long_requests import LongRequestsReport
from djavError.widgets.notifications_report import NotificationsReport
from djavError.widgets.too_many_queries_requests import (
    TooManyQueriesRequestsReport)
from djavError.widgets.trigger_errors import TriggerErrors


@user_passes_test(lambda u: u.is_superuser)
def errors(request):
  return _error_base(request, ERRORS, ErrorsReport(request.GET))


@user_passes_test(lambda u: u.is_superuser)
def notifications(request):
  return _error_base(
      request, NOTIFICATIONS, NotificationsReport(request.GET))


@user_passes_test(lambda u: u.is_superuser)
def long_requests(request):
  return _error_base(
      request, LONG_REQUESTS, LongRequestsReport(request.GET))


@user_passes_test(lambda u: u.is_superuser)
def too_many_queries(request):
  return _error_base(
      request, TOO_MANY_QUERIES, TooManyQueriesRequestsReport(request.GET))


@user_passes_test(lambda u: u.is_superuser)
def trigger_errors(request):
  return _error_base(
      request, TRIGGER_ERRORS, TriggerErrors(request, request.POST))


def _error_base(request, current_view_name, the_one_thing_on_the_page):
  context = nav_context(
      current_view_name,
      the_one_thing_on_the_page=the_one_thing_on_the_page)
  return render(request, 'error_base.html', context)


@user_passes_test(lambda u: u.is_superuser)
@ajax_endpoint
def all_fixed(request, model_name, pks):
  model = model_from_name(model_name, subclass_of=Fixable)
  pks = [int(id) for id in pks.split(',')]
  model.allowed_by_user(request.user).filter(pk__in=pks).update(fixed=now())


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
