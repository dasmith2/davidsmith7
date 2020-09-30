from djaveAPI.ajax_or_api_endpoint import ajax_or_api_endpoint_authenticated
from djaveAPI.get_request_variable import get_request_variable
from djaveAPI.models.user_api_key import UserAPIKey
from djaveAPI.to_json import to_json_dict
from djaveAPI.views.api import do_list_or_save_new


@ajax_or_api_endpoint_authenticated
def list_or_save_new_api_key(request_method, request_dict, credentials):
  if request_method == 'POST':
    username = get_request_variable(request_dict, 'username')
    del request_dict['username']
    return to_json_dict(UserAPIKey.objects.create_key(
        username, credentials.user, **request_dict))
  return do_list_or_save_new(
      request_method, request_dict, credentials, 'UserAPIKey')
