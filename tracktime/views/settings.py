from django.shortcuts import render, reverse
from djaveAPI.widgets.new_api_key_widget import NewAPIKeyWidget
from djaveAPI.widgets.new_user_api_key_table import NewUserAPIKeyTable
from djaveLogin.calc_urls import get_logout_url

from tracktime.views.util import tracktime_context


def settings(request):
  table = NewUserAPIKeyTable(request.user, request.POST)
  description = (
      'User API Keys will retrieve data based on what you, the user, can '
      'see on the website.')
  user_api_key_widget = NewAPIKeyWidget(
      request, table, 'User API Keys', description)

  context = tracktime_context(
      'settings_tracktime', request,
      email=request.user.email,
      logout_url=get_logout_url(request),
      user_api_key_widget=user_api_key_widget,
      api_docs_url=reverse('api_docs'))
  return render(request, 'settings_tracktime.html', context)
