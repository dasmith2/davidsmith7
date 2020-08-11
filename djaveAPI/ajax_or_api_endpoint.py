import base64

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.middleware.csrf import CsrfViewMiddleware

from djaveAllowed.credentials import UserCredentials
from djaveAPI.get_request_dict import get_request_dict
from djaveAPI.models.api_key import APIKey
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
    credentials = self.get_credentials(request)
    if credentials is None:
      return problem_response('This API function requires credentials', 403)
    return self.view_function(
        request.method, get_request_dict(request), credentials, *args,
        **kwargs)

  def get_credentials(self, request):
    uname_pword = self.get_uname_pword_header(request)
    if uname_pword:
      (username, plain_password) = uname_pword
      maybe_user = authenticate(username=username, password=plain_password)
      if maybe_user:
        return UserCredentials(maybe_user)
      maybe_api_key = APIKey.objects.get_api_key(username, plain_password)
      if maybe_api_key:
        return maybe_api_key.as_child_class()
      raise Problem(
          'I do not recognize this username and password', status_code=401)
    if request.user.is_authenticated:
      # In this case we need to check the csrf token.
      csrf_invalid_reason = CsrfViewMiddleware().process_view(
          request, None, (), {})
      if csrf_invalid_reason:
        raise Problem('I was unable to verify the CSRF token')
      return UserCredentials(request.user)

  def get_uname_pword_header(self, request):
    auth_header = request.headers.get('Authorization', None)
    if auth_header:
      weird_formatting_response = Problem((
          'This API uses basic authentication. Server side, I am looking for '
          'a header titled "Authorization" with a value along the lines of '
          '"Basic dW5hbWU6cHdvcmQ=" where that dW5... string is a base 64 '
          'encoded string of your-username:your-password But probably you '
          'just want to use a library.'), status_code=401)
      if auth_header.find('Basic ') == -1:
        raise weird_formatting_response
      auth_header = auth_header.replace('Basic ', '')
      uname_pword_str = base64.b64decode(auth_header).decode('utf-8')
      if uname_pword_str.find(':') == -1:
        raise weird_formatting_response
      (username, plain_password) = uname_pword_str.split(':')
      if not username:
        raise Problem('You did not include a username', status_code=401)
      if not plain_password:
        raise Problem('You did not include a password', status_code=401)
      return (username, plain_password)
