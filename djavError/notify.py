from djavError.models.notification import Notification
from djavEmail.staff_email_sender import StaffEmailSender


class Notifier(object):
  def __init__(self, email_sender=None):
    self.email_sender = email_sender

  def notify(self, to_emails, title, message='', email_sender=None):
    email_sender = email_sender or self.email_sender or StaffEmailSender()
    Notification.objects.notify(to_emails, title, message, email_sender)


def notify(to, title, message=''):
  """ `to` can be a string or a list of strings. """
  return Notifier().notify(to, title, message)
