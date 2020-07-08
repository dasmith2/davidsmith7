"""
In order to play with this in the local shell:

from django.conf import settings
settings.ALWAYS_ALLOW_SEND_MAIL = True
"""
from djavEmail.email_sender import EmailSender
from djavEmail.users_email_config_by_host import users_email_config_by_host


class UserEmailSender(EmailSender):
  def __init__(self, host, send_function=None):
    self.users_email_config = users_email_config_by_host(host)
    super().__init__(send_function=send_function)

  def from_display(self):
    return self.users_email_config.from_display

  def from_username(self):
    return self.users_email_config.from_username

  def from_domain(self):
    return self.users_email_config.from_domain
