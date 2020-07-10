from djavError.tests.models.test_fixable import set_fixable_stuff


def set_staff_email_log_stuff(staff_email_log, **kwargs):
  staff_email_log.title = kwargs.get('title', 'Staff email log title')
  staff_email_log.message = kwargs.get('message', 'Staff email log message')
  staff_email_log.to = kwargs.get('to', 'staff@staff.staff')
  return set_fixable_stuff(staff_email_log, **kwargs)
