from django.http import HttpResponse
from django.shortcuts import redirect
from djaveAPI.get_request_dict import get_request_dict
from djaveLogin.login_required import login_required
from djaveURL import protocol_and_host

from quickbooks2.get_authorization_url import get_authorization_url
from quickbooks2.models import UserCredentials


@login_required
def qb_authorize_callback(request):
  """
  After the user says it's cool if we access their data, Quickbooks will
  redirect the user back here, where we can extract authentication and
  authorization data.
  """
  user_credentials = request.user.usercredentials_or_none
  if not user_credentials:
    user_credentials = UserCredentials(user=request.user)

  user_credentials.code = request.GET.get('code', '')
  user_credentials.state = request.GET.get('state', '')
  user_credentials.realmId = request.GET.get('realmId', '')
  user_credentials.error_response = request.GET.get('error_response', '')
  user_credentials.error_description = request.GET.get('error_description', '')
  user_credentials.raw_response = request.GET.get(
      'raw_response', str(get_request_dict(request)))

  user_credentials.save()

  user_credentials.get_access_and_refresh_tokens(protocol_and_host(request))

  # It's best not to display a page directly because sensitive IDs are in the
  # query string, and any embedded Javascript or whatever could then easily
  # read those IDs.
  return redirect('post_quickbooks_authorization')


@login_required
def post_quickbooks_authorization(request):
  return HttpResponse('You just completed the Quickbooks OAuth flow.')


@login_required
def show_authorization_url(request):
  return HttpResponse('<a href="{}">Quickbooks authorization url</a>'.format(
      get_authorization_url(protocol_and_host(request))))
