from datetime import timedelta
import traceback

from django.conf import settings
from django.db import models
from djaveClassMagic import RmOldManager
from djaveDT import now
from djavError.models.staff_email_log import StaffEmailLog
from djavEmail.staff_email_sender import StaffEmailSender


class ErrorManager(RmOldManager):
  def log_error(
      self, title, message, exc_info, extra_to, always_new_error,
      email_sender=None, supress_stack_trace=False):
    existing = None
    if not always_new_error:
      existing = self.logged_existing_error(title)
      if existing:
        return existing
    new_error = self.create_error(
        title, message, exc_info=exc_info, extra_to=extra_to,
        supress_stack_trace=supress_stack_trace)
    self._email_error_obj(new_error, email_sender=email_sender)
    return new_error

  def logged_existing_error(self, title):
    existing = self.filter(
        title=title, created__gte=now() - timedelta(days=1),
        fixed__isnull=True).first()
    if existing:
      existing.count += 1
      existing.latest = now()
      existing.save()
      if settings.DEBUG:
        print('Incrementing "{}" error count'.format(title))
      return existing

  def create_error(
      self, title, message, exc_info=None, extra_to=None,
      supress_stack_trace=False):
    # Just in case somebody passes a tuple in or whatever as the message.
    message = str(message)

    value_ = None
    traceback_ = None
    if exc_info:
      type_, value_, traceback_ = exc_info
    stack_trace = ''
    if supress_stack_trace:
      stack_trace = ''
    elif traceback_:
      stack_trace = '\n'.join(traceback.format_tb(traceback_))
    else:
      stack_trace = '\n'.join([
          line.strip() for line in traceback.format_stack()])

    error_message = ''
    if value_:
      error_message = value_.__repr__()

    to_emails = [settings.EMAIL_ERRORS_TO]
    if extra_to:
      to_emails.extend(extra_to)

    return self.create(
        title=title,
        count=1,
        latest=now(),
        message=message,
        error_message=error_message,
        stack_trace=stack_trace,
        to=','.join(to_emails))

  def _email_error_obj(self, error, email_sender=None):
    email_sender = email_sender or StaffEmailSender()
    email_message = error.message
    if error.error_message:
      email_message += '\n\n{}'.format(error.error_message)
    if error.stack_trace:
      email_message += '\n\n{}'.format(error.stack_trace)
    subject = '{} on {}'.format(error.title, settings.THIS_SERVERS_BASE_URL)
    if error.to:
      email_sender.send_mail(subject, email_message, error.to.split(','))
    else:
      message = 'This error didnt specify to:\n\n{}'.format(email_message)
      Error.objects.create(title=subject[:250], message=message)


class Error(StaffEmailLog):
  error_message = models.TextField(blank=True, default='')
  stack_trace = models.TextField(blank=True, default='')

  objects = ErrorManager()
