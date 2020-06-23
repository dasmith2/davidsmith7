from random import choice

from djaveTest.web_test import WebTest
from django.template.loader import render_to_string


class WebDemo(WebTest):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.go_slow()

  def go_fast(self):
    self._go_slow = False

  def go_slow(self):
    self._go_slow = True

  def say(self, message):
    if self._go_slow:
      # Literally cause the browser to say the message out loud in a Stephen
      # Hawking voice.
      script = render_to_string(
          'say.js', {'say_this': message.replace("'", r"\'")})
      self.driver.execute_script(script)

  def move_fake_mouse_to_element(self, element, offset_x=10, offset_y=10):
    if self._go_slow:
      location = element.location
      context = {'x': location['x'] + offset_x, 'y': location['y'] + offset_y}
      script = render_to_string('move_fake_mouse.js', context)
      return self.driver.execute_script(script)

  def move_click_type(self, element, keys):
    if self._go_slow:
      self.move_click(element)
      self.move_fake_mouse_to_element(element, 10, 30)
    self.type(element, keys)

  def move_click(self, element, done_talking_click=False):
    if self._go_slow:
      self.move_fake_mouse_to_element(element)
      self.wait_mouse()
      self.hover(element)
      if done_talking_click:
        self.wait_talking()
    element.click()

  def hover(self, element):
    self.driver.execute_script("$(arguments[0]).addClass('hover');", element)

  def type(self, element, keys):
    """ Pretend you're a user painstakingly manually typing in keys """
    for key in keys:
      element.send_keys(key)
      if self._go_slow:
        self.wait(choice(range(5)) / 10.0)

  def wait_talking(self):

    def closure():
      return self._js_variable_undefined_or_true('done_talking')
    self.wait_closure(closure, wait_seconds=20)

  def wait_mouse(self):

    def closure():
      return self._js_variable_undefined_or_true('done_moving_fake_mouse')
    self.wait_closure(closure, wait_seconds=20)

  def _js_variable_undefined_or_true(self, variable_name):
    script = 'return typeof(window.{}) == "undefined" || window.{};'.format(
        variable_name, variable_name)
    return_value = self.driver.execute_script(script)
    return return_value is True

  def sign_up(self, email_address):
    self.say(
        'This is the sign up page. No passwords necessary. I enter my '
        'email and click the button.')
    email_box = self.driver.find_element_by_class_name('email')
    self.move_click_type(email_box, email_address)

    button = self.driver.find_element_by_class_name('email_me')
    self.move_click(button, done_talking_click=True)
    self.say(
        'It emailed me a secure, single-use sign up link. Lets go take a '
        'look.')
    self.wait_talking()
    self.go_to_view(
        'sign_up_email_preview', query_string='to={}'.format(email_address))
    sign_up_link = self.driver.find_element_by_tag_name('a')
    self.say(
        'This is the sign up email. Once I click the link, it will create '
        'an account for me. It should keep me logged in for a very long time.')
    sign_up_link = self.driver.find_element_by_tag_name('a')
    self.move_fake_mouse_to_element(sign_up_link)
    self.wait_mouse()
    self.wait_talking()
    self.click_sign_up_link(email_address)

  def wait(self, seconds):
    if self._go_slow:
      super().wait(seconds)

  def login(self, email_address):
    self.say(
        'Welcome to the login page. No passwords necessary. This will email '
        'you a login link that will keep you logged in for about 10 years.')

    email_box = self.driver.find_element_by_class_name('email')
    self.move_click_type(email_box, email_address)

    button = self.driver.find_element_by_class_name('email_me')
    self.move_fake_mouse_to_element(button)

    self.wait_talking()
    button.click()

    self.say('I will now go check {} and see if there is a login link.'.format(
        email_address))
    self.wait_talking()
    self.wait(0.5)
    self.say('Indeed there is a link! I will now click it.')
    self.wait_talking()
    self.click_login_link(email_address)
