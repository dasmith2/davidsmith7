from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_instance import get_instance
from djaveClass.find_models import model_from_name
from djaveAPI.get_request_variable import get_request_variable
from djaveAllowed.allowed_model import AllowedModel
from djaveAllowed.credentials import UserCredentials
from djaveAPI.save import update

from djaveDT import now


@ajax_endpoint_login_required
def ajax_update(request):
  instance = _get_instance(request)

  update(instance, request.POST, UserCredentials(request.user))


@ajax_endpoint_login_required
def ajax_delete(request):
  instance = _get_instance(request)

  if hasattr(instance, 'deleted'):
    instance.deleted = now()
    instance.save()
  else:
    instance.delete()


def _get_instance(request):
  request_data = request.POST
  model_name = get_request_variable(request_data, 'type')
  pk = get_request_variable(request_data, 'id')
  # I'm very intentionally NOT using djaveAPI.get_publishable_model because
  # this is AJAX and you can do AJAX calls on objects that aren't necessarily
  # in the API. The only thing you actually need here is a model I can check
  # permission on.
  model = model_from_name(model_name, AllowedModel)
  import pdb
  pdb.set_trace()
  credentials = UserCredentials(request.user)
  return get_instance(model, pk, credentials)
