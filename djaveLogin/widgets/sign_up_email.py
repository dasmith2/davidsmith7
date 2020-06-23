import re

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class SignUpEmail(object):
  def __init__(self, sign_up_url, email):
    self.sign_up_url = sign_up_url
    self.email = email

  def preview_html(self):
    as_str = self.as_str().strip().replace('\n', '<br>')
    as_str = re.compile(r'(https[^\s<,]+)').sub(r'<a href="\1">\1</a>', as_str)
    return mark_safe(as_str)

  def subject(self):
    return 'A sign up link for TrackTime.TECH'

  def as_str(self):
    context = {'url': self.sign_up_url, 'email': self.email}
    return render_to_string('sign_up_email.txt', context)
