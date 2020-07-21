from datetime import datetime
from django.conf import settings
from django.db import connection
from django.urls import resolve

from djavError.models import Error, LongRequest, TooManyQueriesRequest


def TrackRequestTimeAndQueriesMiddleware(get_response):
  def middleware(request):
    start = datetime.now()
    start_query_count = len(connection.queries)

    response = get_response(request)

    query_count = len(connection.queries) - start_query_count
    duration_delta = datetime.now() - start
    duration_seconds = (
        duration_delta.seconds + duration_delta.microseconds / 1000000)

    method = request.method
    variables = None
    if method == 'GET':
      variables = request.GET
    elif method == 'POST':
      variables = request.POST
    variables = _variables_to_string(variables)

    if duration_seconds > settings.MAX_ALLOWED_REQUEST_TIME:
      existing = LongRequest.objects.filter(
          path=request.path, method=method, fixed__isnull=True).first()
      if existing:
        existing.increment(duration_seconds)
      else:
        LongRequest.objects.create(
            path=request.path, total_duration=duration_seconds, method=method,
            variables=variables, count=1)

    if query_count > settings.MAX_ALLOWED_DB_QUERIES:
      existing = TooManyQueriesRequest.objects.filter(
          path=request.path, method=method, fixed__isnull=True).first()
      if existing:
        existing.increment(query_count)
      else:
        TooManyQueriesRequest.objects.create(
            path=request.path, total_query_count=query_count, method=method,
            variables=variables, count=1)

    return response
  return middleware


def _variables_to_string(variables):
  if variables is None:
    return variables
  if hasattr(variables, 'dict'):
    variables = variables.dict()
  if 'csrfmiddlewaretoken' in variables:
    del variables['csrfmiddlewaretoken']
  del_keys = [key for key in variables.keys() if variables[key] in [None, '']]
  for key in del_keys:
    del variables[key]
  return str(variables)


class LogExceptionsMiddleware:
  def __init__(self, get_response):
    self.get_response = get_response

  def __call__(self, request):
    return self.get_response(request)

  def process_exception(self, request, exception):
    view_name = resolve(request.path).url_name
    title = '{} at {}'.format(type(exception).__name__, view_name)
    message = 'url: {}'.format(request.path)
    # Just a quick and dirty reverse engineering of sys.exc_info() I do it this
    # way so the tests are valid.
    exc_info = (exception.__class__, exception, exception.__traceback__)
    extra_to = []
    always_new_error = False
    Error.objects.log_error(
        title, message, exc_info, extra_to, always_new_error)
