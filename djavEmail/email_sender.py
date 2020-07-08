""" This is a base class which won't work on its own. If you intend to play in
the shell, you probably want user_email_sender or staff_email_sender. """

from django.conf import settings
from djavEmail.mailgun.api import send as mailgun_send, MailgunException


class EmailSender(object):
  def __init__(self, send_function=None):
    self.send_function = send_function or mailgun_send

  def send_mail(
      self, subject, email_message, to_emails,
      ok_to_do_it_in_dev=False):
    if settings.TEST:
      raise Exception('You should Mock(spec=EmailSender)')
    if isinstance(to_emails, str):
      to_emails = [to_emails]
    if (settings.DEBUG or settings.SHELL) and (
        not settings.ALWAYS_ALLOW_SEND_MAIL):
      print('')
      print(subject)
      print(email_message)
      print('')
    elif settings.PROD or settings.STAGE or ok_to_do_it_in_dev or (
        settings.ALWAYS_ALLOW_SEND_MAIL):
      # I do it in stage too so I can get error emails.
      try:
        self.send_function(
            self.from_display(),
            self.from_username(),
            self.from_domain(),
            to_emails, subject, email_message)
      except MailgunException as ex:
        # If there's a bug in the actual error email code, this hack will
        # simply save an error without attempting to email and therefore
        # retriggering the error thus causing an infinite loop.
        from djavError.models.error import Error
        title = 'Error sending email via Mailgun'
        message = 'Mailgun returned status code {}\n\n{}'.format(
            ex.status_code, ex.response_content)
        if not Error.objects.logged_existing_error(title):
          Error.objects.create_error(title, message)
    else:
      raise Exception('Some unexpected pathway is trying to email!')

  def from_display(self):
    raise NotImplementedError('from_display')

  def from_username(self):
    raise NotImplementedError('from_username')

  def from_domain(self):
    raise NotImplementedError('from_domain')
