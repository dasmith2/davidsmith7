from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse, redirect
from djaveLogin.calc_urls import append_next_url


class base_login_decorator(object):
  def __init__(self, view_function):
    self.view_function = view_function

  def __call__(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      if self.is_allowed(request):
        return self.view_function(request, *args, **kwargs)
      raise PermissionDenied
    return self.redirect_to_login(request)

  def is_allowed(self, request):
    return True

  def redirect_to_login(self, request):
    next_url = request.get_full_path_info()
    return redirect(append_next_url(reverse('djave_login'), next_url))
