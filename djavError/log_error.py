from djavError.models.error import Error


class ErrorLogger(object):
  """ This class exists so I can Mock it so I can write tests that
  make sure errors get logged the way I want. """
  def log_error(
      self, title, message='', exc_info=None, extra_to=None,
      always_new_error=False, email_sender=None, supress_stack_trace=False):
    return Error.objects.log_error(
        title, message, exc_info, extra_to, always_new_error,
        email_sender=email_sender, supress_stack_trace=supress_stack_trace)


def log_error(
    title, message='', exc_info=None, extra_to=None, always_new_error=False,
    email_sender=None, supress_stack_trace=False):
  """
  try:
    whatever()
  except Exception:
    log_error(
        'I tried to whatever', 'here are some details', sys.exc_info())

  This is the simplest approach, but it's not very friendly for testing.

  By default, log_error won't email in the shell. But you can change that if
  you want by doing this in the shell:

  from django.conf import settings
  settings.ALWAYS_ALLOW_SEND_MAIL = True
  from errors.models import log_error
  log_error('hello', 'world')
  """
  return ErrorLogger().log_error(
      title, message=message, exc_info=exc_info, extra_to=extra_to,
      always_new_error=always_new_error, email_sender=email_sender,
      supress_stack_trace=supress_stack_trace)
