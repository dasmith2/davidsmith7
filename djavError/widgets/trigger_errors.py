import time

from django.conf import settings
from django.template.loader import render_to_string
from djavError.models.too_many_queries_request import TooManyQueriesRequest
from djavError.notify import notify
from djaveForm.button import Button
from djaveForm.field import TextField
from djaveForm.form import Form


class TriggerErrorsForm(Form):
  def __init__(self, request_POST):
    self.trigger_server_error_button = Button(
        'Trigger server error', button_type='submit')
    self.trigger_too_many_queries_button = Button(
        'Trigger too many queries', button_type='submit')
    self.trigger_long_request_button = Button(
        'Trigger long request', button_type='submit')
    self.send_notification_button = Button(
        'Send notification', button_type='submit')
    self.send_notification_to = TextField('sendnotificationto', required=False)
    super().__init__([
        self.trigger_server_error_button,
        self.trigger_too_many_queries_button,
        self.trigger_long_request_button,
        self.send_notification_button,
        self.send_notification_to])
    self.feedback = None
    if request_POST:
      self.set_form_data(request_POST)
      if self.trigger_server_error_button.get_was_clicked():
        self.trigger_server_error()
      elif self.trigger_too_many_queries_button.get_was_clicked():
        self.feedback = self.trigger_too_many_queries()
      elif self.trigger_long_request_button.get_was_clicked():
        self.feedback = self.trigger_long_request()
      elif self.send_notification_button.get_was_clicked():
        value = self.send_notification_to.get_value()
        if value:
          self.feedback = self.send_notification(value)
        else:
          self.send_notification_to.set_invalid_reason('Required')

  def trigger_server_error(self):
    return 1 / 0

  def trigger_too_many_queries(self):
    query_count = settings.MAX_ALLOWED_DB_QUERIES + 1
    for i in range(query_count):
      TooManyQueriesRequest.objects.filter(total_query_count__gt=i).count()
    return 'I executed {} queries'.format(query_count)

  def trigger_long_request(self):
    seconds = settings.MAX_ALLOWED_REQUEST_TIME + .1
    time.sleep(seconds)
    return 'I slept for {} seconds'.format(seconds)

  def send_notification(self, to):
    subject = 'Hello world'
    notify(to, subject, message='Blah blah blah')
    return 'I sent an email with the subject "{}" to {}'.format(subject, to)


class TriggerErrors(object):
  def __init__(self, request, request_POST):
    self.request = request
    self.request_POST = request_POST
    self.form = TriggerErrorsForm(request_POST)

  def as_html(self):
    context = {'form': self.form}
    return render_to_string(
        'trigger_errors.html', context, request=self.request)
