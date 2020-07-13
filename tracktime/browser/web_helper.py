class WebHelper(object):
  """ Functions that are particular to tracktime and are useful in multiple
  tests/demos go in here. """
  def __init__(self, web_test):
    self.web_test = web_test
    self.driver = self.web_test.driver

  def create_to_do(self, text, button_clue='todo'):
    self.web_test.type('new_description', text)
    self.web_test.move_click(button_clue, wait_talking=True)

    edit_description = self.web_test.find_with_value('description', text)
    return self.web_test.find_pk(edit_description)

  def set_to_do_hours(self, project_work_session_pk, hours):
    script = "update_field('ProjectWorkSession', {}, 'hours', {});".format(
        project_work_session_pk, hours)
    self.driver.execute_script(script)
