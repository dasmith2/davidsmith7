from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveClassMagic.find_models import model_from_name
from djaveDT import now
from djaveLogin.superuser_required import superuser_required
from djavError.log_error import log_error
from djavError.models.error import Error
from djavError.models.fixable import Fixable
from djavError.nav_context import (
    nav_context, ERRORS, NOTIFICATIONS, LONG_REQUESTS, TOO_MANY_QUERIES,
    TRIGGER_ERRORS)
from djavError.widgets.errors import Errors
from djavError.widgets.long_requests import LongRequests
from djavError.widgets.notifications import Notifications
from djavError.widgets.too_many_queries_requests import TooManyQueriesRequests
from djavError.widgets.trigger_errors import TriggerErrors
from djaveHTML.paragraph import Paragraph


@superuser_required
def errors(request):
  return _error_base(request, ERRORS, Errors())


@superuser_required
def notifications(request):
  return _error_base(request, NOTIFICATIONS, Notifications())


@superuser_required
def long_requests(request):
  report = LongRequests()  # LongRequestsReport(request.GET) DO NOT SUBMIT
  return _error_base(request, LONG_REQUESTS, report)


@superuser_required
def too_many_queries(request):
  one_thing_on_page = None
  if settings.DEBUG:
    one_thing_on_page = TooManyQueriesRequests()
  else:
    one_thing_on_page = Paragraph("""
        Django only logs database queries when settings.DEBUG is True, so this
        won't work here I'm afraid. The best thing to do is to have your web
        test create a bunch of test data so your web test pages get lengthy.
        Then, when the web test runs, if there's a page that executes too many
        database queries, your local machine will log the problem and
        ./code_health.sh will report it to you. Also, pay attention to "Long
        requests" because that works when settings.DEBUG is False and that
        should catch any performance problem including way too many database
        queries.""")
  return _error_base(request, TOO_MANY_QUERIES, one_thing_on_page)


@superuser_required
def trigger_errors(request):
  return _error_base(
      request, TRIGGER_ERRORS, TriggerErrors(request, request.POST))


def _error_base(request, current_view_name, the_one_thing_on_the_page):
  context = nav_context(
      current_view_name,
      the_one_thing_on_the_page=the_one_thing_on_the_page)
  return render(request, 'error_base.html', context)


@superuser_required
@ajax_or_api_endpoint_authenticated
def all_fixed(request_method, request_dict, credentials, model_name, pks):
  model = model_from_name(model_name, subclass_of=Fixable)
  pks = [int(id) for id in pks.split(',')]
  credentials.allowed_list(model).filter(pk__in=pks).update(fixed=now())


@superuser_required
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
      'djavError/templates/js/error.js\n\nuser: {}\n\n{} line {} column {}'
      '\nReferer {}\nStack {}').format(
          request.user, post.get('url', ''),
          post.get('line', ''), post.get('col', ''),
          request.META.get('HTTP_REFERER', ''), post.get('stack', ''))
  subject = post.get('msg', 'Javascript error received')
  log_error(subject, message, supress_stack_trace=True)
  return HttpResponse('ok')


def handler404(request, *args, **argv):
  response = render(request, '404.html', {})
  response.status_code = 404
  return response


def handler500(request, *args, **argv):
  response = render(request, '500.html', {})
  response.status_code = 500
  return response


def handler403(request, *args, **argv):
  response = render(request, '403.html', {})
  response.status_code = 403
  return response
