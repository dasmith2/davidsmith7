from django.http import HttpRequest
from djaveAPI.problem import Problem


def get_obj_from_request_pk(request, model):
  pk = get_request_variable(request, 'pk')
  instance = model.live.filter(pk=pk).first()
  if not instance:
    # Don't status_code=404 because that causes ./manage.py runserver to chuck
    # any helpful information and simply display `Not Found:
    # /api/update_field`. Returning a 200 status code gives the user interface
    # a chance to display this helpful message.
    raise Problem('{} {} does not exist'.format(model.__name__, pk))
  if hasattr(instance, 'as_child_class'):
    instance = instance.as_child_class()
  if hasattr(instance, 'user_allowed'):
    if not instance.user_allowed(request.user):
      raise Problem('You do not have permission to manage this {}'.format(
          model.__name__))
  return instance


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
