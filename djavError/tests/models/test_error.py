from unittest.mock import Mock

from djavEmail.email_sender import EmailSender
from djavError.models.error import Error
from djavError.tests.models.test_staff_email_log import (
    set_staff_email_log_stuff)
from djaveTest.unit_test import TestCase


def get_test_error(**kwargs):
  error = Error(
      error_message=kwargs.get('error_message', 'Error message'),
      stack_trace=kwargs.get('stack_trace', 'Line 1: problems.'))
  return set_staff_email_log_stuff(error, **kwargs)


class ErrorTests(TestCase):
  def test_log_error(self):
    email_sender = Mock(spec=EmailSender)
    for i in range(2):
      Error.objects.log_error(
          'Hello world', 'I message you', exc_info=None, extra_to=None,
          always_new_error=False, email_sender=email_sender)

    self.assertEqual(1, len(email_sender.send_mail.call_args_list))

    self.assertEqual(1, Error.objects.count())
    error = Error.objects.first()
    self.assertEqual(2, error.count)
    self.assertEqual('Hello world', error.title)
