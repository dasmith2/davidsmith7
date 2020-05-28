from django.shortcuts import reverse, redirect
from djaveLogin.calc_urls import append_next_url


class login_required(object):
  def __init__(self, view_function):
    self.view_function = view_function

  def __call__(self, request, *args, **kwargs):
    if request.user.is_authenticated:
      return self.view_function(request, *args, **kwargs)
    next_url = request.get_full_path_info()
    return redirect(append_next_url(reverse('djave_login'), next_url))
