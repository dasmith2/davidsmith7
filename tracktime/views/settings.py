from django.shortcuts import render, reverse
from djaveAPI.widgets.api_keys_widget import APIKeysWidget
from djaveAPI.widgets.user_api_keys_table import UserAPIKeysTable
from djaveLogin.login_required import login_required
from djaveLogin.widgets.settings_widget import (
    SettingsWidget as DjaveLoginSettingsWidget)

from tracktime.views.util import tracktime_context


@login_required
def settings(request):
  table = UserAPIKeysTable(request.user, request.POST)
  description = (
      'User API Keys will retrieve data based on what you, the user, can '
      'see on the website.')
  user_api_key_widget = APIKeysWidget(
      request, table, 'User API Keys', description)
  djave_login_settings_widget = DjaveLoginSettingsWidget(request)

  context = tracktime_context(
      'settings_tracktime',
      user_api_key_widget=user_api_key_widget,
      djave_login_settings_widget=djave_login_settings_widget,
      api_docs_url=reverse('tracktime_api_docs'))
  return render(request, 'settings_tracktime.html', context)
