from djaveLogin.base_login_decorator import base_login_decorator


class superuser_required(base_login_decorator):
  def is_allowed(self, request):
    return request.user.is_superuser
