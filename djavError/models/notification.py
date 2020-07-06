from datetime import timedelta

from django.conf import settings
from djaveClassMagic import RmOldManager
from djaveDT import now
from djavError.models.staff_email_log import StaffEmailLog
from djavEmail.staff_email_sender import StaffEmailSender


class NotificationManager(RmOldManager):
  def notify(self, to_emails, title, message, email_sender=None):
    """ Log to_emails, title, and message. If it's the first we've seen it
    today, send an email as well. """
    email_sender = email_sender or StaffEmailSender()
    if isinstance(to_emails, str):
      to_emails = [to_emails]
    # I had days=1, but what if you want to send a daily notification? Monday
    # it goes out at 3:01am, Tuesday it tries to go out at 3:00am but it
    # doesn't because it went out within the last day.
    existing = self.filter(
        to=str(to_emails), title=title, message=message,
        created__gte=now() - timedelta(hours=23)).first()
    if existing:
      existing.count += 1
      existing.latest = now()
      existing.save()
    else:
      self.create(
          to=str(to_emails), title=title, message=message, count=1,
          latest=now())
      email_sender.send_mail(
          title, message, settings.SERVER_EMAIL, to_emails)


class Notification(StaffEmailLog):
  """ Like Errors, just way less important. """
  objects = NotificationManager()
