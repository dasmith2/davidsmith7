from django.shortcuts import render
from djaveAPI.api_key_ajax import api_key_ajax
from djaveAPI.filters import filter_model
from djaveAPI.model_api_docs import model_api_docs
from djaveAPI.models.api_key import APIKey
from djaveAPI.to_json import to_json_dict
from djaveAPI.widgets.new_api_key_widget import NewAPIKeyWidget
from djaveAPI.widgets.new_user_api_key_table import NewUserAPIKeyTable
from djaveClass.find_models import model_from_name
from djAveJAX import AjaxProblem, ajax_login_required, get_ajax_variable
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


@api_key_ajax
def list_objects(request, api_key, model_name):
  results = []
  model = _get_model(model_name)
  for obj in filter_model(model, api_key, request.GET):
    results.append(to_json_dict(obj))
  return {'results': results}


@api_key_ajax
def get_object(request, api_key, model_name, pk):
  model = _get_model(model_name)

  if request.GET:
    raise AjaxProblem((
        'When getting a single {}, no filters are valid. You '
        'specified {}').format(model_name, ', '.join(request.GET.keys())), 400)

  try:
    instance = model.all.allowed(api_key).filter(pk=pk).first()
  except ValueError as ex:
    # "Field 'id' expected a number but got 'a'."
    if ex.args[0].find('number'):
      raise AjaxProblem('{} is not a valid integer'.format(pk), 400)
  if not instance:
    raise AjaxProblem('There is no {} with id {}'.format(
        model_name, pk), 404)
  return to_json_dict(instance)


def _get_model(model_name):
  model = model_from_name(model_name)
  if not model:
    raise AjaxProblem('There is no {} API'.format(model_name), status_code=404)
  return model


def user_api_keys(request):
  table = NewUserAPIKeyTable(request.user, request.POST)
  description = (
      'User API Keys will retrieve data based on what you, the user, can '
      'see on the website.')
  widget = NewAPIKeyWidget(
      request, table, 'User API Keys', description)
  context = {'the_one_thing_on_this_page': widget}
  return render(request, 'this_site.html', context)


@ajax_login_required
def delete_key(request):
  pk = get_ajax_variable(request.POST, 'pk')
  api_key = APIKey.objects.filter(pk=pk).first()
  if not api_key:
    raise AjaxProblem('This API Key does not exist')
  api_key = api_key.as_child_class()
  if not api_key.can_delete(request.user):
    raise AjaxProblem('You do not have permission to delete this key')
  api_key.delete()
