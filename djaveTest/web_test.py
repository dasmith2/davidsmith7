from abc import abstractmethod
import os
from pathlib import Path
import re
import time

from django.conf import settings
from django.shortcuts import reverse
from djaveAPI.status_codes import is_server_error
from djaveClassMagic.find_models import all_models
from djaveLogin.calc_urls import append_next_url, NEXT_URL
from djaveReport.date_range_report import FROM_DATE, TO_DATE
from djaveURL import dict_as_query
import requests


# all_web_tests means that I don't have to maintain a list of existing web
# tests. I can just scan for them. In order for all_web_tests to work, every
# app's web tests need to be imported into my_specific_app/web_test/__init__.py
# The downside to that is, when unit tests run, the unit test loader ends up
# scanning through all the files and running all the imports. Normally this
# would be fine, but selenium is a special case. It's only needed locally for
# web testing. The last time I tried to deploy it as a dependency to Heroku,
# Heroku freaked out with incomprehensible error messages. Hence we need to do
# this hack where selenium stuff is imported within functions so as to avoid
# import errors when unit tests run as part of continuous integration.


def all_web_tests():
  return all_models(WebTest)


class WebTest(object):
  def __init__(self, server):
    self.server = server
    self.driver = None

  @abstractmethod
  def run(self):
    raise NotImplementedError('run')

  def pre_run(self):
    from selenium import webdriver
    self.driver = webdriver.Firefox()

  def close_driver(self):
    from selenium.common.exceptions import SessionNotCreatedException
    if self.driver:
      try:
        self.driver.close()
      except SessionNotCreatedException:
        # The driver is closed already.
        pass

  def go_to_url(self, url):
    self.driver.get(url)
    self.close_django_toolbar()

  def go_to_view(self, view_name, query_string='', **kwargs):
    url = self.server_plus_reverse(view_name, **kwargs)
    if query_string:
      if query_string[0] != '?':
        url += '?'
      url += query_string
    self.go_to_url(url)

  def go_to_dated_report(self, view_name, from_date, to_date):
    query_string = dict_as_query({
        FROM_DATE: from_date.isoformat(), TO_DATE: to_date.isoformat()})
    self.go_to_view(view_name, query_string=query_string)

  def get_view_json(self, view_name, *args, **kwargs):
    response = requests.get(
        self.server_plus_reverse(view_name, *args, **kwargs))
    if is_server_error(response):
      if self.server == 'http://127.0.0.1:8000':
        raise Exception('Server error. Look at your ./manage.py runserver')
      raise Exception('Server error. Check {}/admin/errors/stayderror/'.format(
          self.server))
    return response.json()

  def server_plus_reverse(self, view_name, *args, **kwargs):
    path = reverse(view_name, args=args, kwargs=kwargs)
    return '{}{}'.format(self.server, path)

  def close_django_toolbar(self):
    from selenium.common.exceptions import NoSuchElementException
    # The debug toolbar gets in the way of elements when you try to click on
    # them sometimes.
    try:
      toolbar = self.driver.find_element_by_id('djDebugToolbar')
      if toolbar.value_of_css_property('display') == 'block':
        self.driver.find_element_by_id('djHideToolBarButton').click()
    except NoSuchElementException:
      pass

  def default_server(self):
    # return settings.STAGE_SERVER is also a common one. Or you can just do
    # ./manage.py my_web_test --server=https://stage.hihoward.com
    return 'http://127.0.0.1:8000'

  def sleep(self, seconds):
    """ Seconds can be a float """
    time.sleep(seconds)

  def wait_for_closure(self, closure, error_message=None, wait_for_seconds=5):
    attempts = 0
    poll_interval = 0.1
    max_attempts = wait_for_seconds / poll_interval
    while attempts < max_attempts and not closure():
      time.sleep(poll_interval)
      attempts += 1
    if not closure():
      raise Exception(error_message or 'Closure was never True')

  def wait_for_class(self, class_name):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    WebDriverWait(self.driver, 10).until(
        expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, class_name)))
    return self.driver.find_element_by_class_name(class_name)

  def wait_for_xpath(self, xpath):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    WebDriverWait(self.driver, 10).until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, xpath)))
    return self.driver.find_element_by_xpath(xpath)

  def wait_for_text(self, xpath, expected_text):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    WebDriverWait(self.driver, 10).until(
        expected_conditions.text_to_be_present_in_element(
            (By.XPATH, xpath), expected_text))
    return self.driver.find_element_by_xpath(xpath)

  def raise_if_on_error_screen(self):
    if 1 == len(self.driver.find_elements_by_id('traceback')):
      message = 'There\'s an on-screen Django error. '
      if settings.LOCAL:
        message += 'Check your ./manage.py runserver. '
      else:
        message += 'Check for server error emails from {}. '.format(
            settings.THIS_SERVERS_BASE_URL)
      message += 'The error message is: {}'.format(
          self.driver.find_element_by_xpath('//div[@id="summary"]/pre').text)
      raise Exception(message)

  def click_button(self, container_or_button_id):
    from selenium.common.exceptions import NoSuchElementException
    try:
      button = self.driver.find_element_by_xpath(
          '//*[@id="{}"]//*[@class="button"]'.format(container_or_button_id))
    except NoSuchElementException:
      button = self.driver.find_element_by_xpath(
          '//*[@id="{}"]'.format(container_or_button_id))
    assert button.is_displayed()
    button.click()

  def screen_height(self):
    return self.driver.execute_script('return window.screen.height;')

  def scrolled_to(self):
    return self.driver.execute_script('return window.pageYOffset;')

  def is_scrolled_to(self, element):
    scrolled_to = self.scrolled_to()
    screen_height = self.screen_height()
    above = scrolled_to < element.location['y']
    below = scrolled_to + screen_height >= element.location['y']
    return above and below

  def img_path(self, img_file_name):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    app_dir = Path(this_dir).parent.as_posix()
    img_dir = os.path.join(app_dir, 'static')
    return os.path.join(img_dir, img_file_name)

  def do_file_upload(self, container, img_path):
    id_upload = container.find_element_by_xpath('.//input[@type="file"]')
    id_upload.send_keys(img_path)

  def login(self, email_address):
    self.driver.find_element_by_class_name('email').send_keys(email_address)
    self.driver.find_element_by_class_name('emailmealoginlink').click()
    self.click_login_link(email_address)

  def click_login_link(self, email_address):
    find_login_token_url = '{}?email={}'.format(
        self.server_plus_reverse('login_token'), email_address)
    token = requests.get(find_login_token_url).json()['token']
    next_url_finder = re.compile('{}=(.+)'.format(NEXT_URL))
    next_url = next_url_finder.findall(self.driver.current_url)[0]
    login_url = self.server_plus_reverse('djave_login', token=token)
    self.go_to_url(append_next_url(login_url, next_url))
