from unittest.mock import Mock

from django.shortcuts import reverse
from djavEmail.user_email_sender import UserEmailSender
from djaveLogin.widgets.login_email import LoginEmail
from djaveTest.unit_test import TestCase, get_test_user


class SignUpEmailTests(TestCase):
  def test_send(self):
    user = get_test_user()

    user_email_sender = Mock(spec=UserEmailSender)
    email = LoginEmail(
        'https', 'tracktime.tech', user,
        next_url=reverse('sign_up_email_preview'),
        user_email_sender=user_email_sender)
    email.send()
    self.assertEqual(1, len(user_email_sender.send_mail.call_args_list))
