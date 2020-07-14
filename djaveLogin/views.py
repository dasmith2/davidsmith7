import sys

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import redirect, reverse, render
from djaveAPI.ajax_endpoint import ajax_endpoint
from djaveAPI.problem import Problem
from djavError.log_error import log_error
from djaveLogin.forms import LoginForm
from djaveLogin.calc_urls import NEXT_URL, append_next_url
from djaveLogin.models import (
    new_login_url, new_sign_up_url, LoginToken)
from djaveLogin.widgets.sign_up_email import SignUpEmail
from djaveLogin.widgets.login_email import LoginEmail
from djaveURL import is_valid_url


@ajax_endpoint
def login_token(request):
  """ This is for local webtests basically. I need to automatically log in
  without actually checking email or examining the output of ./manage.py
  runserver """
  if settings.LOCAL:
    if 'email' in request.GET:
      email = request.GET['email']
      login_token = None

      user = User.objects.filter(email=email).first()
      if user:
        login_token = LoginToken.objects.filter(
            user=user, used__isnull=True).first()
      else:
        login_token = LoginToken.objects.filter(
            email=email, used__isnull=True).first()

      if login_token:
        return {'token': login_token.token}
      else:
        raise Problem(
            'I could not find an unused token for {}'.format(email))
    else:
      raise Problem('I expect an email query string variable')
  else:
    raise Problem('This view is only for local development')


def sign_up(request, token=None):
  return login_sign_up_helper(
      request, 'sign_up.html', token=token, login_mode=False)


def login(request, token=None):
  return login_sign_up_helper(
      request, 'log_in.html', token=token, login_mode=True)


def login_sign_up_helper(request, template, token=None, login_mode=True):
  possible_used_up_token = False
  if token:
    # The user clicked a login link
    user = auth.authenticate(request, token=token)
    if user:
      if user.is_active:
        auth.login(request, user)
        ten_years = 10 * 365 * 24 * 60 * 60
        request.session.set_expiry(ten_years)
        if login_mode:
          return redirect(_post_login_url(request))
        else:
          return redirect(settings.GO_TO_VIEW_AFTER_SIGN_UP)
      else:
        return render(request, 'inactive_user.html')
    else:
      possible_used_up_token = True

  # The user may want to send themselves a login or sign up link
  form = LoginForm(request.POST, login_mode=login_mode)
  send_to_email = form.get_email()
  sent = bool(send_to_email)
  if sent:
    user = User.objects.filter(email=send_to_email).first()
    next_url = _next_url(request)
    if settings.LOCAL:
      if user:
        print('\n{}\n'.format(new_login_url(
            user, 'http', '127.0.0.1:8000', next_url=next_url)))
      else:
        print('\n{}\n'.format(new_sign_up_url(
            send_to_email, 'http', '127.0.0.1:8000')))
    else:
      if user:
        LoginEmail(
            'https', request.get_host(), user, next_url=next_url).send()
      else:
        SignUpEmail('https', request.get_host(), send_to_email).send()
    form = LoginForm(None, login_mode=login_mode)

  # If the user tried to log in but used an expired token, they'll stay stuck
  # on this page and get a friendly message to generate a new link. So they're
  # about to submit a form with a new email address, but the useless token is
  # still in the URL at that point.
  login_url = _login_url_no_token(request)
  sign_up_url = reverse('djave_sign_up')
  post_to = login_url if login_mode else sign_up_url
  default_header = 'Login' if login_mode else 'Sign up'
  return render(request, template, context={
      'email_text_box': form.email_text_box,
      'email_me_button': form.email_me_button,
      'email_sent_to': send_to_email,
      'possible_used_up_token': possible_used_up_token,
      'post_to': post_to,
      'default_header': default_header,
      'sent': sent,
      'sign_up_url': reverse('djave_sign_up'),
      'login_url': reverse('djave_login')})


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


def sign_up_email_preview(request):
  to = request.GET.get('to', 'example@gmail.com')
  email = SignUpEmail('https', 'tracktime.tech', to)
  context = {
      'to': to,
      'subject': email.subject(),
      'email': email.preview_html()}
  return render(request, 'djaveLogin_email_preview.html', context)
