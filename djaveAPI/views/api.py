from djaveAPI.api_endpoint import api_endpoint
from djaveAPI.filters import filter_model, get_filters
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.get_instance import get_instance
from djaveAPI.get_publishable_model import get_publishable_model
from djaveAPI.get_posted_json import get_posted_json
from djaveAPI.problem import Problem
from djaveAPI.save import update, save_new
from djaveAPI.to_json import to_json_dict


@api_endpoint
def list_or_save_new(request, api_key, model_name):
  model = get_publishable_model(model_name)
  if request.method == 'GET':
    return paged_results(
        model, filter_model(model, api_key, request.GET),
        page=get_page(request.GET))
  elif request.method in ['POST', 'PUT']:
    instance = save_new(model, get_posted_json(request), api_key)
    return to_json_dict(instance, model)
  else:
    raise Problem((
        'This API endpoint is not sure what to do with the {} '
        'request method').format(request.method))


@api_endpoint
def get_or_save_existing(request, api_key, model_name, pk):
  model = get_publishable_model(model_name)

  filters = get_filters(model, request.GET)
  filter_field_names = [f.filter_field.name for f in filters]
  if filter_field_names:
    raise Problem((
        'When getting or saving a single {}, no filters are valid. You '
        'specified {}').format(model_name, ', '.join(filter_field_names)), 400)

  instance = get_instance(model, pk, api_key)
  if request.method == 'POST':
    update(instance, get_posted_json(request), api_key)
  elif request.method == 'DELETE':
    instance.mark_deleted()
  return to_json_dict(instance, model)
