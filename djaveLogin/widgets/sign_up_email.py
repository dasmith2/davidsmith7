
from django.template.loader import render_to_string
from djaveLogin.widgets.email_base import EmailBase
from djaveLogin.models import new_sign_up_url


class SignUpEmail(EmailBase):
  def __init__(self, protocol, host, email):
    super().__init__(protocol, host)
    self.email = email

  def to(self):
    return self.email

  def subject(self):
    return 'A sign up link for {}'.format(self.get_site_name())

  def as_str(self):
    url = new_sign_up_url(self.email, self.protocol, self.host)
    context = {
        'url': url, 'email': self.email, 'site_name': self.get_site_name()}
    return render_to_string('sign_up_email.txt', context)
