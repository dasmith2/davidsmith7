from djaveForm.button import Button
from djaveForm.field import TextField
from djaveForm.form import Form


class LoginForm(Form):
  def __init__(self, request_POST, login_mode=True):
    self.email_text_box = TextField('email', required=True)
    button_text = 'Email me a {} link'.format(
        'login' if login_mode else 'sign up')
    self.email_me_button = Button(
        button_text, key_prefix='email_me', button_type='submit')
    super().__init__([self.email_text_box, self.email_me_button])

    self._email = None
    if request_POST and self.a_button_was_clicked(request_POST):
      self.set_form_data(request_POST)
      self._email = self.email_text_box.get_value()

  def get_email(self):
    return self._email
