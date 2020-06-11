from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_instance import get_instance
from djaveAPI.get_model import get_model
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.models.credentials import UserCredentials
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
  model = get_model(model_name)
  credentials = UserCredentials(request.user)
  return get_instance(model, pk, credentials)
