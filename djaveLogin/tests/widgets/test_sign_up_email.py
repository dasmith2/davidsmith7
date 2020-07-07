from unittest.mock import Mock

from djavEmail.user_email_sender import UserEmailSender
from djaveLogin.widgets.sign_up_email import SignUpEmail
from djaveTest.unit_test import TestCase


class SignUpEmailTests(TestCase):
  def test_send(self):
    user_email_sender = Mock(spec=UserEmailSender)
    email = SignUpEmail(
        'https', 'tracktime.tech', 'bob@user.com',
        user_email_sender=user_email_sender)
    email.send()
    self.assertEqual(1, len(user_email_sender.send_mail.call_args_list))
