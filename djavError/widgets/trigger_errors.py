from django.template.loader import render_to_string
from djaveForm.button import Button
from djaveForm.form import Form


class TriggerErrorsForm(Form):
  def __init__(self, request_POST):
    self.trigger_server_error_button = Button(
        'Trigger server error', button_type='submit')
    super().__init__([self.trigger_server_error_button])
    if request_POST:
      self.set_form_data(request_POST)
      if self.trigger_server_error_button.get_was_clicked():
        self.trigger_server_error()

  def trigger_server_error(self):
    return 1 / 0


class TriggerErrors(object):
  def __init__(self, request, request_POST):
    self.request = request
    self.request_POST = request_POST
    self.form = TriggerErrorsForm(request_POST)

  def as_html(self):
    context = {'form': self.form}
    return render_to_string(
        'trigger_errors.html', context, request=self.request)
