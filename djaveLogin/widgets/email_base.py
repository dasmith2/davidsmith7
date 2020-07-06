import re

from django.utils.safestring import mark_safe
from djavEmail.users_email_config_by_host import users_email_config_by_host
from djavEmail.user_email_sender import UserEmailSender


class EmailBase(object):
  def __init__(self, protocol, host, user_email_sender=None):
    self.protocol = protocol
    self.host = host
    self.user_email_sender = user_email_sender or UserEmailSender(self.host)

  def get_site_name(self):
    return users_email_config_by_host(self.host).site_name

  def to(self):
    raise NotImplementedError('to')

  def subject(self):
    raise NotImplementedError('subject')

  def as_str(self):
    raise NotImplementedError('as_str')

  def preview_html(self):
    as_str = self.as_str().strip().replace('\n', '<br>')
    as_str = re.compile(r'(https[^\s<,]+)').sub(r'<a href="\1">\1</a>', as_str)
    return mark_safe(as_str)

  def send(self):
    self.user_email_sender.send_mail(self.subject(), self.as_str(), self.to())
