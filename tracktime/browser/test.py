import requests
from requests.auth import HTTPBasicAuth

from tracktime.browser.demo import Demo


class Test(Demo):
  def run(self):
    self.go_fast()
    super().run()

  def demo_sign_up(self):
    self.go_to_view('tracktime_api_docs')
    self.find_with_text('h1', 'Welcome')
    self.go_to_view('tracktime_homepage')
    super().demo_sign_up()

  def do_stuff(self):
    super().do_stuff()
    self.find('not_done')

  def api_key(self):
    self.say_move_type('input.username', 'daves_data', """
        Here you can create an API key.""")
    self.say_move_type('input.webhook_url', 'https://your.website', """
        If you specify a webhook url, Track Time dot tech will send data to
        your computers whenever your data changes.""")
    self.move_click('button.savenew')
    api_key_username = self.find('tbody td.username').text
    api_key_password = self.find('span.plain_password').text
    self.web_test_the_api(HTTPBasicAuth(api_key_username, api_key_password))

  def api(self):
    self.api_key()

    self.say_move_click('api_docs', """
        Now that I have an API key username and password, let me explain the
        significance.""")
    self.say("""
        The API gives you the option to hire your own software engineers to
        write custom code that searches, reads, edits, or deletes your data
        according to your own logic.""", wait=True)
    self.say_scroll(self.find_with_text('h1', 'ManualLineItem'), """
        For example you could dynamically add line items to your invoices.""")
    self.say_scroll(self.find_with_text('h1', 'ProjectInvoice'), """
        You could write an automation that bugs your customers for overdue
        invoices.""")
    self.say_scroll(self.find_with_text('h1', 'Welcome'), """
        You're limited only by your imagination and the competence of
        your engineers.""")

  def web_test_the_api(self, http_basic_auth):
    existing_project = self.web_test_list(http_basic_auth)
    creator = existing_project['creator']
    new_project = self.web_test_save_new(http_basic_auth, creator)
    self.web_test_get_one(http_basic_auth, new_project)
    self.web_test_update(http_basic_auth, new_project)
    self.web_test_delete(http_basic_auth, new_project)

  def web_test_list(self, http_basic_auth):

    def _get_project_list(url):
      projects = requests.get(url, auth=http_basic_auth).json()['results']
      first_name = projects[0]['name']
      options = [self.bobs, self.hotel]
      if first_name not in options:
        raise Exception(
            'I expected {} to be in {}'.format(first_name, options))
      return projects[0]
    url = self._list_or_save_new_url()
    project = _get_project_list(url)
    url += '?creator={}&page=1'.format(project['creator'])
    return _get_project_list(url)

  def web_test_save_new(self, http_basic_auth, creator):
    url = self.server_plus_reverse('list_or_save_new', model_name='Project')
    data = {
        'creator': 'me', 'name': 'The Grand Hotel', 'use_clock': True,
        'has_to_do_list': False}
    new_project = requests.post(url, json=data, auth=http_basic_auth).json()
    assert new_project['name'] == 'The Grand Hotel'
    assert new_project['use_clock']
    assert not new_project['has_to_do_list']
    return new_project

  def web_test_get_one(self, http_basic_auth, project):
    url = self._get_save_or_delete_existing_url(project['id'])
    got_name = requests.get(url, auth=http_basic_auth).json()['name']
    assert project['name'] == got_name

  def web_test_update(self, http_basic_auth, project):
    url = self._get_save_or_delete_existing_url(project['id'])
    data = {'name': 'The EXTRA Grand Hotel'}
    project = requests.post(url, json=data, auth=http_basic_auth).json()
    assert project['name'] == 'The EXTRA Grand Hotel'

  def web_test_delete(self, http_basic_auth, project):
    url = self._get_save_or_delete_existing_url(project['id'])
    assert requests.delete(url, auth=http_basic_auth).json()['OK']

  def _list_or_save_new_url(self):
    return self.server_plus_reverse('list_or_save_new', model_name='Project')

  def _get_save_or_delete_existing_url(self, pk):
    return self.server_plus_reverse(
        'get_save_or_delete_existing', model_name='Project', pk=pk)
