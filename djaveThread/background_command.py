import sys
import traceback

from django.conf import settings
from djaveDT import now
from djavError.log_error import log_error
from djavEmail.staff_email_sender import StaffEmailSender
from djaveThread.models import LoggedCommand
from rq import Queue

from worker import conn


# The default default_timeout is 2 minutes. This makes it an hour.
q = Queue(connection=conn, default_timeout=60 * 60)


def background_command(func):
  """ Use this decorator on a function that's probably kicked off by clock.py
  This a) runs your code in the background and b) logs the start time, end
  time, and when applicable, error to the LoggedCommand table. """
  def func_wrapper(*args, **kwargs):
    if settings.TEST or settings.SHELL:
      # Tests and the shell should just run immediately and not catch any
      # errors.
      return func(*args, **kwargs)
    elif settings.DEBUG or settings.BACKGROUND:
      command_name = func.__name__
      command_run = LoggedCommand.objects.create(
          command_name=command_name, started=now())
      results = None
      try:
        results = func(*args, **kwargs)
        command_run.completed = now()
      except Exception:
        exc_info = sys.exc_info()
        command_run.error = log_error(
            '{} error'.format(command_name), exc_info=exc_info)
        if settings.DEBUG:
          type_, value_, traceback_ = exc_info
          print(value_.__repr__())
          print('\n'.join(traceback.format_tb(traceback_)))
      command_run.save()
      return results
    else:
      # Otherwise we're on web or something and we wanna kick this function
      # off to a background thread.
      q.enqueue(func, *args, **kwargs)
  return func_wrapper


@background_command
def test_error():
  print(1 / 0)


@background_command
def test_email():
  StaffEmailSender().send_mail(
      'Test background command email', 'Hey it worked!', settings.ADMINS)
