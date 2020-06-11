from django.shortcuts import render
from djaveAPI.ajax_endpoint import ajax_endpoint_login_required
from djaveAPI.get_request_variable import get_obj_from_request_pk
from djaveAPI.models.api_key import APIKey
from djaveAPI.widgets.api_keys_widget import APIKeysWidget
from djaveAPI.widgets.user_api_keys_table import UserAPIKeysTable


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
  get_obj_from_request_pk(request, APIKey).delete()
