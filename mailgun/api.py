from django.conf import settings
import requests


def send(from_display, from_username, from_domain, to, subject, text):
  if not from_display or not from_username or not from_domain:
    raise Exception((
        'from_display {}, from_username {}, and from_domain {} are all '
        'required').format(from_display, from_username, from_domain))
  url = 'https://api.mailgun.net/v3/{}/messages'.format(from_domain)
  auth = requests.auth.HTTPBasicAuth('api', settings.MAILGUN_API_KEY)
  data = {
      'from': '{} <{}@{}>'.format(from_display, from_username, from_domain),
      'to': to,
      'subject': subject,
      'text': text}
  return requests.post(url, auth=auth, data=data)
