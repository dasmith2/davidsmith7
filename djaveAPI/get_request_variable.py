from django.http import HttpRequest
from djaveAPI.get_request_dict import get_request_dict
from djaveAPI.problem import Problem


def get_request_variable(data_or_request, variable_name, required=True):
  """ data_or_request can be a dictionary such as request.POST, or it can just
  be a request. """
  data = data_or_request
  if isinstance(data, HttpRequest):
    data = get_request_dict(data_or_request)
  if variable_name not in data:
    if required:
      raise Problem(
          'This request doesn\'t specify a {}'.format(variable_name))
    return None
  variable = data[variable_name]
  if required and variable in [None, '']:
    raise Problem('The {} is required'.format(variable_name))
  return variable
