class WebHelper(object):
  """ Functions that are particular to tracktime and are useful in multiple
  tests/demos go in here. """
  def __init__(self, web_test):
    self.web_test = web_test
    self.driver = self.web_test.driver

  def set_to_do_hours(self, project_work_session_pk, hours):
    script = "update_field('ProjectWorkSession', {}, 'hours', {});".format(
        project_work_session_pk, hours)
    self.driver.execute_script(script)
