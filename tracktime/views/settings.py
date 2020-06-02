from django.shortcuts import render, reverse
from djaveAPI.widgets.api_keys_widget import APIKeysWidget
from djaveAPI.widgets.user_api_keys_table import UserAPIKeysTable
from djaveLogin.calc_urls import get_logout_url

from tracktime.views.util import tracktime_context


def settings(request):
  table = UserAPIKeysTable(request.user, request.POST)
  description = (
      'User API Keys will retrieve data based on what you, the user, can '
      'see on the website.')
  user_api_key_widget = APIKeysWidget(
      request, table, 'User API Keys', description)

  context = tracktime_context(
      'settings_tracktime', request,
      email=request.user.email,
      logout_url=get_logout_url(request),
      user_api_key_widget=user_api_key_widget,
      api_docs_url=reverse('api_docs'))
  return render(request, 'settings_tracktime.html', context)
