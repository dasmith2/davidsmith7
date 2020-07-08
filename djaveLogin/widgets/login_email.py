from django.template.loader import render_to_string
from djaveLogin.widgets.email_base import EmailBase
from djaveLogin.models import new_login_url


class LoginEmail(EmailBase):
  def __init__(
      self, protocol, host, user, next_url=None, user_email_sender=None):
    super().__init__(protocol, host, user_email_sender=user_email_sender)
    self.user = user
    self.next_url = next_url

  def to(self):
    return self.user.email

  def subject(self):
    return 'A login link for {}'.format(self.get_site_name())

  def as_str(self):
    url = new_login_url(
        self.user, self.protocol, self.host, next_url=self.next_url)
    context = {
        'url': url, 'email': self.user.email,
        'site_name': self.get_site_name()}
    return render_to_string('login_email.txt', context)
