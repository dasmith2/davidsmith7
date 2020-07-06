from django.conf import settings
from djavEmail.users_email_config import UsersEmailConfig


def users_email_config_by_host(host):
  if not hasattr(settings, 'USERS_EMAIL_LOOKUP'):
    raise Exception(
        'I am expecting you to have a dictionary called USERS_EMAIL_LOOKUP in '
        'your settings whose keys are domains and whose values are instances '
        'of djavEmail.users_email_config.UsersEmailConfig')
  for key in settings.USERS_EMAIL_LOOKUP:
    if key.lower().find(host.lower()) >= 0:
      value = settings.USERS_EMAIL_LOOKUP[key]
      if not isinstance(value, UsersEmailConfig):
        raise Exception((
            'settings.USERS_EMAIL_LOOKUP["{}"] should be a UsersEmailConfig, '
            'but it is a {}').format(key, value.__class__))
      return value
  raise Exception(
      'Unable to find {} in settings.USERS_EMAIL_LOOKUP'.format(host))
