from djavError.models.notification import Notification
from djavError.tests.models.test_staff_email_log import (
    set_staff_email_log_stuff)


def get_test_notification(**kwargs):
  return set_staff_email_log_stuff(Notification(), **kwargs)
