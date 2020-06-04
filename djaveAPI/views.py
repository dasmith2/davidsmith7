import json

from django.shortcuts import render
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.api_endpoint import api_endpoint
from djaveAPI.discover_schema import publishable_model_from_name
from djaveAPI.filters import filter_model, get_filters
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.model_api_docs import model_api_docs
from djaveAPI.models.api_key import APIKey
from djaveAPI.paged_results import paged_results, get_page
from djaveAPI.problem import Problem
from djaveAPI.save import update, save_new, delete
from djaveAPI.to_json import to_json_dict
from djaveAPI.widgets.api_keys_widget import APIKeysWidget
from djaveAPI.widgets.user_api_keys_table import UserAPIKeysTable
from djaveForm.field import URLField
from djaveURL import protocol_and_host


def generic_api_docs(request, model_names):
  model_docs = api_doc_contents(request, model_names)
  return render(request, 'api_docs.html', context={'model_docs': model_docs})


def api_doc_contents(request, model_names):
  api_root_url = protocol_and_host(request)
  model_docs = []
  for model_name in model_names:
    model_docs.append(model_api_docs(model_name, api_root_url))
  return model_docs


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


def user_api_keys(request):
  table = UserAPIKeysTable(request.user, request.POST)
  description = (
      'User API Keys will retrieve data based on what you, the user, can '
      'see on the website.')
  widget = APIKeysWidget(
      request, table, 'User API Keys', description)
  context = {'the_one_thing_on_this_page': widget}
  return render(request, 'this_site.html', context)


@ajax_endpoint_login_required
def delete_key(request):
  _ajax_api_key(request).delete()


@ajax_endpoint_login_required
def update_webhook_url(request):
  api_key = _ajax_api_key(request)
  api_key.webhook_url = get_request_variable(request.POST, 'webhook_url')
  url_field = URLField('webhook_url', required=False)
  url_field.set_value(api_key.webhook_url)
  why_not_valid = url_field.explain_why_not_valid()
  if why_not_valid:
    raise Problem(why_not_valid)
  api_key.save()


def _ajax_api_key(request):
  pk = get_request_variable(request.POST, 'pk')
  api_key = APIKey.objects.filter(pk=pk).first()
  if not api_key:
    raise Problem('This API Key does not exist')
  api_key = api_key.as_child_class()
  if not api_key.user_can_manage_me(request.user):
    raise Problem('You do not have permission to manage this key')
  return api_key
