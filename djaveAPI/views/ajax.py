from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_request_ajax_obj
from djaveAllowed.credentials import UserCredentials
from djaveAPI.save import update

from djaveDT import now


@ajax_endpoint_login_required
def ajax_update(request):
  instance = get_request_ajax_obj(request)
  update(instance, request.POST, UserCredentials(request.user))


@ajax_endpoint_login_required
def ajax_delete(request):
  instance = get_request_ajax_obj(request)

  if hasattr(instance, 'deleted'):
    instance.deleted = now()
    instance.save()
  else:
    instance.delete()
