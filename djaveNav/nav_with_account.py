""" The difference between nav and nav_with_account is nav_with_account puts
account stuff to the right of the navigation. So you'll probably want to use
this for your top level navigation. """
from django.shortcuts import reverse
from djaveLogin.models import append_next_url
from djaveNav.nav import Nav


class NavWithAccount(Nav):
  def __init__(self, nav_list, current_view_name, request):
    super().__init__(nav_list, current_view_name)
    self.request = request

  def template(self):
    return 'nav_with_account.html'

  def context(self):
    context = super().context()
    context['describe_user'] = self.request.user.email
    context['logout_url'] = append_next_url(
        reverse('djave_logout'), self.request.get_full_path())
    return context
