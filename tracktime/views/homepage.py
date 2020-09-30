from django.conf import settings
from django.shortcuts import render, reverse
from djaveHTML.a import AButton

from tracktime.views.nav_context import tracktime_nav


def homepage(request):
  logged_in_user_button = None
  if request.user.is_authenticated:
    first_nav = tracktime_nav(
        request.user, None).first_nav_item_current_or_not()
    logged_in_user_button = AButton(first_nav.display, first_nav.url)
  context = {
      'logged_in': request.user.is_authenticated,
      'logged_in_user_button': logged_in_user_button,
      'login_url': reverse('djave_login'),
      'sign_up_url': reverse('djave_sign_up'),
      'api_docs_url': reverse('tracktime_api_docs'),
      'show_video': not settings.WEB_TEST}
  return render(request, 'tracktime_homepage.html', context)
