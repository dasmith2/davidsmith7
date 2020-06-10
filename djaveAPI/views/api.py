import json

from djaveAPI.api_endpoint import api_endpoint
from djaveAPI.find_models import publishable_model_from_name
from djaveAPI.filters import filter_model, get_filters
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.problem import Problem
from djaveAPI.save import update, save_new, delete
from djaveAPI.to_json import to_json_dict


@api_endpoint
def list_or_save_new(request, api_key, model_name):
  model = _get_model(model_name)
  if request.method == 'GET':
    return paged_results(
        model, filter_model(model, api_key, request.GET),
        page=get_page(request.GET))
  elif request.method == 'POST':
    instance = save_new(model, posted_json(request), api_key, model)
    return to_json_dict(instance, model)
  else:
    raise Problem((
        'This API endpoint is not sure what to do with the {} '
        'request method').format(request.method))


@api_endpoint
def get_or_save_existing(request, api_key, model_name, pk):
  model = _get_model(model_name)

  filters = get_filters(model, request.GET)
  filter_field_names = [f.filter_field.name for f in filters]
  if filter_field_names:
    raise Problem((
        'When getting or saving a single {}, no filters are valid. You '
        'specified {}').format(model_name, ', '.join(filter_field_names)), 400)

  try:
    instance = model.allowed(api_key).filter(pk=pk).first()
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise Problem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise Problem((
        'Either there is no {} with id {}, or this API '
        'Key does not have permission to access it.').format(
            model_name, pk), 404)
  if request.method == 'POST':
    update(instance, posted_json(request), api_key, model)
  elif request.method == 'DELETE':
    delete(instance, model)
  return to_json_dict(instance, model)


def posted_json(request):
  try:
    return json.loads(request.body)
  except json.decoder.JSONDecodeError:
    raise Problem('The request contained invalid JSON')


def _get_model(model_name):
  model = publishable_model_from_name(model_name)
  if not model:
    raise Problem(
        'There is no {} API'.format(model_name), status_code=404)
  return model
