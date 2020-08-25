import base64

from django.contrib.auth import authenticate
from django.middleware.csrf import CsrfViewMiddleware
from djaveAllowed.credentials import UserCredentials

from djaveAPI.models.api_key import APIKey
from djaveAPI.problem import Problem


def get_credentials(request):
  uname_pword = get_uname_pword_header(request)
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


def get_uname_pword_header(request):
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
