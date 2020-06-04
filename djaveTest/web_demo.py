from random import choice
import time

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
      self.driver.execute_script(script)

  def demo_move_click_type(self, element, keys):
    if self._go_slow:
      self.move_fake_mouse_to_element(element)
      self.wait_for_done_moving_fake_mouse()
      element.click()
      self.move_fake_mouse_to_element(element, 10, 30)
    self.demo_type(element, keys)

  def demo_type(self, element, keys):
    """ Pretend you're a user painstakingly manually typing in keys """
    for key in keys:
      element.send_keys(key)
      if self._go_slow:
        time.sleep(choice(range(5)) / 10.0)

  def wait_for_done_talking(self):

    def closure():
      return self._js_variable_undefined_or_true('done_talking')
    self.wait_for_closure(closure, wait_for_seconds=20)

  def wait_for_done_moving_fake_mouse(self):

    def closure():
      return self._js_variable_undefined_or_true('done_moving_fake_mouse')
    self.wait_for_closure(closure, wait_for_seconds=20)

  def _js_variable_undefined_or_true(self, variable_name):
    script = 'return typeof(window.{}) == "undefined" || window.{};'.format(
        variable_name, variable_name)
    return self.driver.execute_script(script) is True

  def login(self, email_address):
    self.say(
        'Welcome to the login page. No passwords necessary. This will email '
        'you a login link that will keep you logged in for about 10 years.')

    email_box = self.driver.find_element_by_class_name('email')
    self.demo_move_click_type(email_box, email_address)

    button = self.driver.find_element_by_class_name('emailmealoginlink')
    self.move_fake_mouse_to_element(button)

    self.wait_for_done_talking()
    button.click()

    self.say('I will now go check {} and see if there is a login link.'.format(
        email_address))
    self.wait_for_done_talking()
    self.sleep(0.5)
    self.say('Indeed there is a link! I will now click it.')
    self.wait_for_done_talking()
    self.click_login_link(email_address)
