from datetime import datetime, date
from urllib.parse import urlparse, parse_qsl, urlencode

from django.http import HttpRequest
from django.shortcuts import reverse


def admin_edit_url(my_object):
  view_name = 'admin:{}_{}_change'.format(
      my_object._meta.app_label, my_object._meta.model_name)
  return reverse(view_name, args=[my_object.pk])


def get_full_path_from_request(request_get_full_path):
  # request_get_full_path can be a request object or a string.
  if isinstance(request_get_full_path, str):
    return request_get_full_path
  elif isinstance(request_get_full_path, HttpRequest):
    return request_get_full_path.get_full_path()
  raise Exception('I am not sure what to do with a {}'.format(
      request_get_full_path.__class__))


def url_with_date(request_get_full_path, day=None):
  # request_get_full_path can be a request object or a string.
  path = get_full_path_from_request(request_get_full_path)
  day = day or date.today()
  return url_with(path, day=date_to_url_str(day))


def date_from_url(request_get_full_path):
  # If there isn't a day in the query string, return today.
  # request_get_full_path can be a request object or a string.
  path = get_full_path_from_request(request_get_full_path)
  default_str = date_to_url_str(date.today())
  date_str = query_as_dict(path).get('day', default_str)
  return url_str_to_date(date_str)


def query_as_dict(request_get_full_path):
  # request_get_full_path can be a request object or a string.
  path = get_full_path_from_request(request_get_full_path)
  url = urlparse(path)
  path = url.path  # /dashboard/
  query_str = url.query  # date=2018-02-15&building_id=1
  # {'day': '2018-02-15', 'building_id': '1'}
  return dict(parse_qsl(query_str))


def url_with(request_get_full_path, **kwargs):
  # Add the given key value pairs to the query string. Why is this so hard haha
  # request_get_full_path can be a request object or a string.
  path = get_full_path_from_request(request_get_full_path)
  url = urlparse(path)
  path = url.path  # /dashboard/
  query = query_as_dict(path)
  for key, value in kwargs.items():
    if value is None:
      if key in query:
        del query[key]
    else:
      query[key] = str(value)
  query = urlencode(query)
  if query:
    return '{}?{}'.format(path, query)
  return path


def date_to_url_str(dte):
  return dte.strftime(DATE_FORMAT)


DATE_FORMAT = '%Y-%m-%d'


def url_str_to_date(date_str):
  """ dl hardcoded 09-31-2017 in the url one time. That should just do the
  right thing and return what he meant, the last day in September, 2017-09-30.
  """
  while True:
    try:
      return datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError as ex:
      if len(ex.args) and ex.args[0] == 'day is out of range for month':
        parts = date_str.split('-')
        date_str = '-'.join((parts[0], str(int(parts[1]) - 1), parts[2]))
      else:
        raise ex
