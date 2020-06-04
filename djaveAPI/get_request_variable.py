from django.http import HttpRequest
from djaveAPI.problem import Problem


def get_request_variable(data, variable_name, required=True):
  """ data can be a dictionary such as request.POST, or it can just be a
  request. """
  if isinstance(data, HttpRequest):
    data = get_data_from_request(data)
  if variable_name not in data:
    if required:
      raise Problem(
          'This request doesn\'t specify a {}'.format(variable_name))
    return None
  variable = data[variable_name]
  if required and variable in [None, '']:
    raise Problem('The {} is required'.format(variable_name))
  return variable


def get_data_from_request(request):
  return request.POST or request.PUT or request.DELETE
