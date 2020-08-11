from django.http import HttpResponse

from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.filters import filter_model
from djaveAPI.find_models import allowed_model_from_name
from djaveAPI.get_instance import get_instance
from djaveAPI.models.pretend_publishable import PretendPublishable
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.problem import Problem
from djaveAPI.save import update, save_new
from djaveAPI.to_json import to_json_dict


@ajax_or_api_endpoint_authenticated
def list_or_save_new(request_method, request_dict, credentials, model_name):
  model = allowed_model_from_name(model_name)
  if request_method == 'GET':
    return paged_results(
        model, filter_model(model, credentials, request_dict),
        page=get_page(request_dict))
  elif request_method in ['POST', 'PUT']:
    if 'id' in request_dict:
      raise Problem(
          'When saving a new {}, you should not specify an id'.format(
              model_name))
    if 'type' in request_dict and request_dict['type'] != model_name:
      raise Problem((
          'Your URL specifies model {} but the data you posted includes a '
          'type variable that says {}').format(
              model_name, request_dict['type']))
    instance = save_new(model, request_dict, credentials)
    return to_json_dict(instance, model)
  else:
    raise Problem((
        'This API endpoint is not sure what to do with the {} '
        'request_method').format(request_method))


@ajax_or_api_endpoint_authenticated
def get_save_or_delete_existing(
    request_method, request_dict, credentials, model_name, pk):
  """ Well, get_save_or_delete_existing """
  model = allowed_model_from_name(model_name)

  instance = get_instance(model_name, model.objects, pk, credentials)
  if request_method == 'POST':
    update(instance, request_dict, credentials)
  elif request_method == 'DELETE':
    if hasattr(instance, 'mark_deleted'):
      instance.mark_deleted()
    else:
      instance.delete()
  return to_json_dict(instance, model)


def api_root(request):
  return HttpResponse('Welcome to the root of the API.')


def get_request_api_obj(model, pk, credentials):
  instance = None
  try:
    find_with_model = model
    if issubclass(model, PretendPublishable):
      find_with_model = model.actually_publishing()
    instance = credentials.allowed_list(find_with_model).filter(pk=pk).first()
    if issubclass(model, PretendPublishable):
      instance = model(instance)
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise Problem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise Problem((
        'Either there is no {} with id {}, or your credentials '
        'do not have permission to access it.').format(
            model.__name__, pk), 404)
  return instance
