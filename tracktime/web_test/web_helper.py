class WebHelper(object):
  """ Functions that are particular to tracktime and are useful for both demos
  and web tests go in here. """
  def __init__(self, web_test):
    self.web_test = web_test
    self.driver = self.web_test.driver

  def create_project(self, name):
    self.web_test.move_click_type(self.find('new_name'), name)
    save_button = self.find('savenew')
    self.web_test.move_click(save_button)

  def find(self, clue):
    elts = self.driver.find_elements_by_class_name(clue)
    if len(elts):
      return elts[0]
    elts = self.driver.find_elements_by_tag_name(clue)
    if len(elts):
      return elts[0]
    raise Exception('I was unable to find {}'.format(clue))
