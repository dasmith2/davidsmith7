from django.shortcuts import render, reverse
from djaveAPI.widgets.user_api_keys import UserAPIKeys
from djaveStyle.widgets.zoom_preference import ZoomPreference
from djaveLogin.login_required import login_required
from djaveLogin.widgets.settings_widget import (
    SettingsWidget as DjaveLoginSettingsWidget)

from tracktime.views.nav_context import SETTINGS, tracktime_context


@login_required
def settings(request):
  djave_login_settings_widget = DjaveLoginSettingsWidget(
      request.get_full_path(), request.user)
  zoom_preference = ZoomPreference(request, request.POST, request.user)

  user_api_keys = UserAPIKeys(reverse(SETTINGS))

  context = tracktime_context(
      request.user, SETTINGS,
      zoom_preference=zoom_preference,
      user_api_keys=user_api_keys,
      djave_login_settings_widget=djave_login_settings_widget,
      api_docs_url=reverse('tracktime_api_docs'))
  return render(request, 'settings_tracktime.html', context)
