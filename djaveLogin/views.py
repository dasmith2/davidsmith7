import sys

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, reverse, render
from djavError.models import log_error
from djaveLogin.forms import LoginForm
from djaveLogin.models import NEXT_URL, new_login_url, append_next_url
from djaveURL import is_valid_url


def login(request, token=None):
  # The user clicked a login link
  possible_used_up_token = False
  if token:
    user = auth.authenticate(request, token=token)
    if user:
      if user.is_active:
        auth.login(request, user)
        ten_years = 10 * 365 * 24 * 60 * 60
        request.session.set_expiry(ten_years)
        return redirect(_post_login_url(request))
      else:
        return render(request, 'inactive_user.html')
    else:
      possible_used_up_token = True

  # The user may want to send themselves a login link
  form = LoginForm(request.POST)
  send_to_email = form.get_email()
  if send_to_email:
    user = User.objects.filter(email=send_to_email).first()
    if user:
      login_url = new_login_url(user, request, next_url=_next_url(request))
      if settings.LOCAL:
        print('Pretend I sent an email to {} with this login link:\n{}'.format(
            send_to_email, login_url))
      else:
        raise Exception('I dont know how to send an email to users yet!!')
    form = LoginForm(None)

  # If the user tried to log in but used an expired token, they'll stay stuck
  # on this page and get a friendly message to generate a new link. So they're
  # about to submit a form with a new email address, but the useless token is
  # still in the URL at that point.
  post_to = _login_url_no_token(request)
  return render(request, 'how_to_log_in.html', context={
      'email_text_box': form.email_text_box,
      'email_me_button': form.email_me_button,
      'email_sent_to': send_to_email,
      'possible_used_up_token': possible_used_up_token,
      'post_to': post_to})


def logout(request):
  auth.logout(request)
  return redirect(_login_url_no_token(request))


def _login_url_no_token(request):
  return append_next_url(reverse('djave_login'), _next_url(request))


def _next_url(request):
  return request.GET.get(NEXT_URL)


def _post_login_url(request):
  next_url = _next_url(request)
  if next_url:
    # Make sure nobody can do, like, ?next=http://malicious.com
    if is_valid_url(next_url):
      return next_url
    else:
      log_error('Got a weird next_url', next_url, sys.exc_info())
  return '/'
