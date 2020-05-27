from django.shortcuts import render
from djaveAPI.api_key_ajax import api_key_ajax
from djaveAPI.filters import filter_model
from djaveAPI.model_api_docs import model_api_docs
from djaveAPI.to_json import to_json_dict
from djaveClass.find_models import model_from_name
from djAveJAX import AjaxProblem


def generic_api_docs(request, model_names, api_root_url):
  model_docs = []
  for model_name in model_names:
    model_docs.append(model_api_docs(model_name, api_root_url))
  return render(request, 'api_docs.html', context={'model_docs': model_docs})


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
