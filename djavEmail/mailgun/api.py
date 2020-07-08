from django.conf import settings
import requests


class MailgunException(Exception):
  def __init__(self, status_code, response_content):
    self.status_code = status_code
    self.response_content = response_content
    super().__init__(status_code, response_content)


def send(from_display, from_username, from_domain, to, subject, text):
  if not settings.MAILGUN_API_KEY:
    raise MailgunException(401, (
        'You need to put MAILGUN_API_KEY in Heroku\'s config vars for this '
        'site'))
  if not from_display or not from_username or not from_domain:
    raise Exception((
        'from_display {}, from_username {}, and from_domain {} are all '
        'required').format(from_display, from_username, from_domain))
  url = 'https://api.mailgun.net/v3/mg.{}/messages'.format(from_domain)
  auth = requests.auth.HTTPBasicAuth('api', settings.MAILGUN_API_KEY)
  data = {
      'from': '{} <{}@{}>'.format(from_display, from_username, from_domain),
      'to': to,
      'subject': subject,
      'text': text}
  got = requests.post(url, auth=auth, data=data)
  if got.status_code != 200:
    raise MailgunException(got.status_code, got.content.decode('utf-8'))
  return True
