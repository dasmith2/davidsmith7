from django.conf import settings
from djavEmail.email_sender import EmailSender


class StaffEmailSender(EmailSender):
  """
  I put this in an object so you can mock and verify in tests if you want to
  make super sure you're going to get that staff email.

  What if the very thing that's broken is sending email, and you want to
  experiment in the shell? Do this:

  from django.conf import settings
  settings.ALWAYS_ALLOW_SEND_MAIL = True

  Now when you log_error(...) for instance it'll actually send the email even
  though you're in the shell. """

  def from_display(self):
    return settings.STAFF_EMAIL_FROM_DISPLAY

  def from_username(self):
    return settings.STAFF_EMAIL_FROM_USERNAME

  def from_domain(self):
    return settings.STAFF_EMAIL_FROM_DOMAIN
