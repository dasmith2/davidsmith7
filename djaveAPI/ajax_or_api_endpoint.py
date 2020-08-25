
from django.http import JsonResponse

from djaveAPI.get_credentials import get_credentials
from djaveAPI.get_request_dict import get_request_dict
from djaveAPI.problem import Problem
from djaveAPI.response import problem_response, OK_RESPONSE


class ajax_or_api_endpoint(object):
  """ This decorator goes on functions whose data is either a form post, or
  posted json. No user information is handed to the view. If you require
  information about who made the request, use
  ajax_or_api_endpoint_authenticated which will pass credentials along to the
  view. Decorated views will get called like so:

  @ajax_or_api_endpoint
  def my_view(request_method, request_dict, *args, **kwargs): """
  def __init__(self, view_function):
    self.view_function = view_function
    # This is a bit hacky! I basically copied it from csrf_exempt in
    # django.views.decorators.csrf
    self.csrf_exempt = True

  def __call__(self, request, *args, **kwargs):
    try:
      return self.response_as_ajax(self.get_response(request, *args, **kwargs))
    except Problem as ex:
      return problem_response(ex)

  def get_response(self, request, *args, **kwargs):
    return self.view_function(
        request.method, get_request_dict(request), *args, **kwargs)

  def response_as_ajax(self, response):
    if isinstance(response, JsonResponse):
      return response
    elif response is None:
      return OK_RESPONSE
    return JsonResponse(response)


class ajax_or_api_endpoint_authenticated(ajax_or_api_endpoint):
  """ This decorator goes on functions that could accept either a logged in
  user, an auth header that specifies a user's username and password, or an
  auth header that specifies an API key. The data can be either a form post, or
  posted json.

  The decorated view will get called like so:

  @ajax_or_api_endpoint_authenticated
  def my_view(request_method, request_dict, credentials, *args, **kwargs):
  """
  def get_response(self, request, *args, **kwargs):
    credentials = get_credentials(request)
    if credentials is None:
      return problem_response('This API function requires credentials', 403)
    return self.view_function(
        request.method, get_request_dict(request), credentials, *args,
        **kwargs)
