""" Include this widget on your settings page for all login related stuff such
as a logout everywhere link. """
from django.template.loader import render_to_string
from djaveLogin.calc_urls import get_logout_url


class SettingsWidget(object):
  def __init__(self, request):
    self.request = request

  def as_html(self):
    context = {
        'logout_url': get_logout_url(self.request),
        'email': self.request.user.email}
    return render_to_string('djave_login_settings_widget.html', context)

  def __str__(self):
    return self.as_html()
