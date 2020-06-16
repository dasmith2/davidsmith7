from django.http import HttpRequest
from djaveAllowed.allowed_model import AllowedModel
from djaveAllowed.credentials import UserCredentials
from djaveAPI.get_instance import get_instance
from djaveAPI.problem import Problem
from djaveClass.find_models import model_from_name


def get_request_ajax_obj(request, model=None, pk=None):
  if not pk:
    pk = get_request_variable(request, 'pk')
  model_name = None
  if model:
    model_name = model.__name__
  else:
    model_name = get_request_variable(request.POST, 'type')
    # I'm very intentionally NOT using djaveAPI.get_publishable_model because
    # this is AJAX and you can do AJAX calls on objects that aren't necessarily
    # in the API. The only thing you actually need here is a model I can check
    # permission on.
    model = model_from_name(model_name, AllowedModel)
  credentials = UserCredentials(request.user)

  # model.live is really handy for pulling back a list of active objects. This
  # requires a single object and I don't want to outsmart myself, so I'm just
  # using model.objects
  return get_instance(model_name, model.objects, pk, credentials)


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
